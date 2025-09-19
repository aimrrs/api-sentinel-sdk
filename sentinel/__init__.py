import requests
import threading
from functools import wraps, reduce
import operator

from .errors import BudgetExceededError

__all__ = [
    "init",
    "wrap",
    "BudgetExceededError",
]

# --- Global State ---
_SENTINEL_CONFIG = {
    "api_key": None,
    "backend_url": "http://127.0.0.1:8000", "https://api-sentinel-backend.onrender.com/"
    "project_id": None,
    "monthly_budget": 0,
    "current_usage": 0,
    "usd_to_inr_rate": 83.50,
    "pricing_cache": {}, 
}

# --- Public Functions ---
def init(api_key: str):
    """
    Initializes the Sentinel SDK.
    Fetches generic state (budget, usage, rate) but NOT specific pricing.
    """
    if not api_key or not api_key.startswith("sentinel_pk_"):
        raise ValueError("A valid Sentinel API key (sentinel_pk_...) is required.")

    _SENTINEL_CONFIG["api_key"] = api_key
    
    print("SENTINEL: Verifying key and fetching initial state...")
    try:
        headers = {"X-Sentinel-Key": api_key}
        response = requests.get(
            f"{_SENTINEL_CONFIG['backend_url']}/keys/verify",
            headers=headers, timeout=5
        )
        response.raise_for_status()
        data = response.json()
        _SENTINEL_CONFIG.update({
            "project_id": data["project_id"],
            "monthly_budget": data["monthly_budget"],
            "current_usage": data["current_usage"],
            "usd_to_inr_rate": data["usd_to_inr_rate"],
        })
        print("SENTINEL: Initialization successful. State is synced.")
    except requests.RequestException as e:
        raise RuntimeError(f"SENTINEL: Could not connect to backend to initialize. Error: {e}")

def wrap(client, adapter):
    """
    Wraps an API client. This function is now fully generic and dynamic.
    """
    if not _SENTINEL_CONFIG["api_key"]:
        raise RuntimeError("Sentinel SDK has not been initialized. Please call sentinel.init() first.")

    # Lazy load the pricing for this specific API on the first wrap call
    _fetch_and_cache_pricing_for_api(adapter.api_name)

    # Dynamically get the original method using the adapter's specified path
    original_method = _get_nested_attr(client, adapter.method_path)

    @wraps(original_method)
    def _sentinel_wrapper(*args, **kwargs):
        if _SENTINEL_CONFIG["current_usage"] >= _SENTINEL_CONFIG["monthly_budget"]:
            raise BudgetExceededError(f"Project budget of {_SENTINEL_CONFIG['monthly_budget']} exceeded.")
        
        response = original_method(*args, **kwargs)
        
        try:
            usage_data = adapter.get_usage_and_cost(response)
            cost = usage_data["cost"]
            _SENTINEL_CONFIG["current_usage"] += cost
            threading.Thread(target=_report_usage_to_backend, args=(usage_data,)).start()
        except Exception as e:
            print(f"SENTINEL WARNING: Could not process usage. Error: {e}")
        return response

    # Dynamically replace the original method with our new wrapper
    _set_nested_attr(client, adapter.method_path, _sentinel_wrapper)
    return client

# --- Private Helper Functions ---

def _get_nested_attr(obj, path):
    """Gets a nested attribute from an object using a dot-separated string."""
    return reduce(getattr, path.split('.'), obj)

def _set_nested_attr(obj, path, value):
    """Sets a nested attribute on an object using a dot-separated string."""
    parts = path.split('.')
    parent = reduce(getattr, parts[:-1], obj)
    setattr(parent, parts[-1], value)

def _fetch_and_cache_pricing_for_api(api_name: str):
    """
    Fetches and caches the pricing for a specific API, but only if it hasn't been fetched yet.
    """
    if api_name in _SENTINEL_CONFIG["pricing_cache"]:
        return

    print(f"SENTINEL: Fetching latest pricing for '{api_name}'...")
    try:
        pricing_response = requests.get(
            f"{_SENTINEL_CONFIG['backend_url']}/v1/public/pricing/{api_name}",
            timeout=5
        )
        pricing_response.raise_for_status()
        pricing_data = pricing_response.json()
        
        formatted_pricing = {
            item["model_name"]: {
                "input": item["input_cost_per_million_usd"],
                "output": item["output_cost_per_million_usd"]
            } for item in pricing_data
        }
        _SENTINEL_CONFIG["pricing_cache"][api_name] = formatted_pricing
        print(f"SENTINEL: Pricing for '{api_name}' is now cached.")
    except requests.RequestException as e:
        print(f"SENTINEL WARNING: Could not fetch pricing for {api_name}. Costs may be inaccurate. Error: {e}")

def _report_usage_to_backend(usage_data):
    """Sends the usage data to the Sentinel backend API."""
    try:
        headers = {"X-Sentinel-Key": _SENTINEL_CONFIG["api_key"]}
        response = requests.post(
            f"{_SENTINEL_CONFIG['backend_url']}/v1/usage",
            json=usage_data, headers=headers, timeout=5
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"SENTINEL WARNING: Could not report usage to backend. Error: {e}")
