from .base import BaseAdapter

class OpenAIAdapter(BaseAdapter):
    """
    Adapter for handling responses from the OpenAI API client.
    It knows how to parse the response, count tokens, and calculate cost.
    """

    # Pricing per 1 million tokens (as of Sep 2025, for example)
    # This should be updated as OpenAI's pricing changes.
    MODEL_PRICING = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    def get_usage_and_cost(self, response):
        """
        Processes a successful OpenAI API response object to extract usage and cost.

        Args:
            response: The successful ChatCompletion object from the openai library.

        Returns:
            A dictionary with the cost and detailed usage metadata.
        """
        # 1. Extract the raw data from the response object
        usage_data = response.usage
        model_name = response.model
        
        input_tokens = usage_data.prompt_tokens
        output_tokens = usage_data.completion_tokens

        # 2. Calculate the cost using the specific model's pricing
        cost = self._calculate_openai_cost(
            input_tokens,
            output_tokens,
            model_name
        )

        # 3. Return the data in the standardized format required by BaseAdapter
        return {
            "cost": cost,
            "usage_metadata": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model_name,
            }
        }

    def _calculate_openai_cost(self, input_tokens, output_tokens, model_name):
        """
        Calculates the cost based on the token counts and the model used.
        """
        # Find the pricing for the model, defaulting to a zero-cost model if unknown
        pricing = self.MODEL_PRICING.get(model_name, {"input": 0, "output": 0})
        
        # Calculate cost for input and output tokens separately
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        total_cost_usd = input_cost + output_cost
        
        # For an Indian startup, we might want to convert to INR.
        # For the MVP, we can use a hardcoded exchange rate.
        # A real product would use a live currency conversion API.
        usd_to_inr_rate = 83.50
        total_cost_inr = total_cost_usd * usd_to_inr_rate

        return round(total_cost_inr, 4) # Return cost rounded to 4 decimal places