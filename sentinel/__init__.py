from .errors import BudgetExceededError

__all__ = [
    "init",
    "wrap",
    "BudgetExceededError",
]

import requests
import threading
from functools import wraps

# --- Global State ---
# This will hold the configuration and state for the SDK.
_SENTINEL_CONFIG = {
    "api_key": None,
    "backend_url": "http://127.0.0.1:8000", # The URL of FastAPI backend
    "project_id": None, # Will be fetched from the backend
    "monthly_budget": 0,
    "current_usage": 0,
}

# --- Public Functions ---
def init(api_key: str):
    """
    Initializes the Sentinel SDK.
    This verifies the key with the backend and fetches the current budget state.
    """
    if not api_key or not api_key.startswith("api-sentinel_pk_"):
        raise ValueError("A valid Sentinel API key (api-sentinel_pk_...) is required.")

    _SENTINEL_CONFIG["api_key"] = api_key

    print("[API - SENTINEL] Verifying key and fetching latest budget...")
    try:
        headers = {"X-Sentinel-Key": api_key}
        response = requests.get(
            f"{_SENTINEL_CONFIG['backend_url']}/keys/verify",
            headers=headers,
            timeout=5
        )
        response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)

        # Update the local state with the data from the backend
        data = response.json()
        _SENTINEL_CONFIG["project_id"] = data["project_id"]
        _SENTINEL_CONFIG["monthly_budget"] = data["monthly_budget"]
        _SENTINEL_CONFIG["current_usage"] = data["current_usage"]

        print("SENTINEL: Initialization successful. Budget is ready.")

    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid Sentinel API key. Please check your key on the dashboard.") from e
        else:
            raise RuntimeError(f"[API - SENTINEL] Could not connect to backend. Status: {e.response.status_code}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"[API - SENTINEL] Could not connect to backend. Network error: {e}") from e

def wrap(client, adapter):
    """
    Wraps an API client to add Sentinel's monitoring and budget control.

    Args:
        client: The original API client instance (e.g., openai.OpenAI()).
        adapter: The specific adapter for this client (e.g., OpenAIAdapter()).

    Returns:
        The same client instance, but with its primary method "wrapped".
    """
    if not _SENTINEL_CONFIG["api_key"]:
        raise RuntimeError("Sentinel SDK has not been initialized. Please call sentinel.init() first.")

    # This is a bit of Python magic. For OpenAI, we are replacing the
    # 'client.chat.completions.create' method with our own wrapper function.
    original_method = client.chat.completions.create

    @wraps(original_method)
    def _sentinel_wrapper(*args, **kwargs):
        # 1. --- Pre-call Budget Check ---
        if _SENTINEL_CONFIG["current_usage"] >= _SENTINEL_CONFIG["monthly_budget"]:
            raise BudgetExceededError(
                f"Project has exceeded its budget of {_SENTINEL_CONFIG['monthly_budget']}."
            )

        # 2. --- Make the Original API Call ---
        response = original_method(*args, **kwargs)

        # 3. --- Post-call Processing (using the adapter) ---
        try:
            usage_data = adapter.get_usage_and_cost(response)
            cost = usage_data["cost"]
            
            # Update local usage state immediately
            _SENTINEL_CONFIG["current_usage"] += cost

            # 4. --- Report to Backend Asynchronously ---
            # We use a separate thread so it doesn't slow down the user's app
            threading.Thread(
                target=_report_usage_to_backend,
                args=(usage_data,)
            ).start()

        except Exception as e:
            # If our adapter fails, we don't want to crash the user's app.
            # We just log it and continue.
            print(f"SENTINEL WARNING: Could not process usage. Error: {e}")

        # 5. --- Return the Original Response ---
        return response

    # Replace the original method with our new wrapper
    client.chat.completions.create = _sentinel_wrapper
    return client


# --- Private Helper Functions ---

def _report_usage_to_backend(usage_data):
    """Sends the usage data to the Sentinel backend API."""
    try:
        headers = {"X-Sentinel-Key": _SENTINEL_CONFIG["api_key"]}
        response = requests.post(
            f"{_SENTINEL_CONFIG['backend_url']}/v1/usage",
            json=usage_data,
            headers=headers,
            timeout=5 # Set a timeout to avoid hanging
        )
        response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)
    except requests.RequestException as e:
        # In a real product, we would have a more robust retry mechanism.
        print(f"SENTINEL WARNING: Could not report usage to backend. Error: {e}")