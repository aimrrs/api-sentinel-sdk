# API Sentinel SDK

API Sentinel SDK is a Python library designed to provide seamless integration with the API Sentinel platform, enabling developers to monitor, secure, and analyze their API usage with ease.

## Features
- Easy integration with the API Sentinel platform
- Adapters for different API providers (e.g., OpenAI)
- Error handling utilities
- Extensible adapter base for custom integrations

## Installation

You can install the SDK using pip:

```bash
pip install api-sentinel-sdk
```

Or, if you are developing locally:

```bash
pip install -e .
```

## Usage

Here's a basic example of how to use the SDK:

```python
from sentinel.adapters.openai import OpenAIAdapter

# Initialize the adapter
adapter = OpenAIAdapter(api_key="your-api-key")

# Make a request
response = adapter.send_request({
    "prompt": "Hello, world!",
    "max_tokens": 5
})

print(response)
```

## Project Structure

```
sentinel/
    __init__.py
    errors.py
    adapters/
        __init__.py
        base.py
        openai.py
```

- `adapters/`: Contains adapter classes for different API providers.
- `errors.py`: Custom error classes for the SDK.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author
[aimrrs](https://github.com/aimrrs)



