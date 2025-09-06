class BaseAdapter:
    """
    This is the base class for all API adapters.
    It defines the required methods that a specific adapter
    must implement to be compatible with the Sentinel SDK.
    """

    def get_usage_and_cost(self, response):
        """
        Processes a successful API response object to extract usage and cost.

        Args:
            response: The successful response object from the third-party API client.

        Returns:
            A dictionary with the following structure:
            {
                "cost": float,
                "usage_metadata": dict
            }
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(
            "Each adapter must implement the 'get_usage_and_cost' method."
        )