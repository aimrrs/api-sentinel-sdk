class BaseAdapter:
    """
    This is the base class for all API adapters.
    It defines the required methods and attributes that a specific adapter
    must implement to be compatible with the Sentinel SDK.
    """
    # NEW: Every adapter must now declare its unique API name
    api_name: str = "unknown"

    # NEW: Every adapter must now declare the path to the method it wants to wrap
    # This is a string like "chat.completions.create"
    method_path: str = ""

    def get_usage_and_cost(self, response):
        """
        Processes a successful API response object to extract usage and cost.
        """
        raise NotImplementedError(
            "Each adapter must implement the 'get_usage_and_cost' method."
        )