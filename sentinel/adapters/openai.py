from .base import BaseAdapter
from .. import _SENTINEL_CONFIG

class OpenAIAdapter(BaseAdapter):
    """
    Adapter for handling responses from the OpenAI API client.
    It now specifies which API it's for and which method to wrap.
    """
    # --- IMPLEMENTING THE NEW REQUIREMENTS ---
    api_name = "openai"
    method_path = "chat.completions.create"
    # --- END OF NEW REQUIREMENTS ---

    def get_usage_and_cost(self, response):
        """
        Processes a successful OpenAI API response object to extract usage and cost.
        """
        usage_data = response.usage
        model_name = response.model
        
        input_tokens = usage_data.prompt_tokens
        output_tokens = usage_data.completion_tokens

        cost = self._calculate_openai_cost(
            input_tokens,
            output_tokens,
            model_name
        )

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
        Calculates cost using the dynamically fetched pricing from the central config.
        """
        # Get the pricing for 'openai' from the central cache
        model_pricing_dict = _SENTINEL_CONFIG["pricing_cache"].get(self.api_name, {})
        pricing = model_pricing_dict.get(model_name, {"input": 0, "output": 0})
        
        input_cost_usd = (input_tokens / 1_000_000) * pricing["input"]
        output_cost_usd = (output_tokens / 1_000_000) * pricing["output"]
        
        total_cost_usd = input_cost_usd + output_cost_usd
        
        usd_to_inr_rate = _SENTINEL_CONFIG["usd_to_inr_rate"]
        total_cost_inr = total_cost_usd * usd_to_inr_rate

        return round(total_cost_inr, 4)

