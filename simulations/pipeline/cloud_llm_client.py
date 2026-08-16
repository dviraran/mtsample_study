"""
Cloud LLM client for comparing case processing across different APIs.
Supports: OpenAI (GPT), Google (Gemini), OpenRouter (Claude, Grok, etc.),
DeepSeek, and Kimi (Moonshot).
"""

import os
import json
import logging
import time
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables — prefer the project .env (current working tree),
# fall back to ~/.env, then to ~/Documents/medbar/.env for users with the
# legacy single-shared-env setup. The project .env wins because dev
# credentials and per-branch Supabase pointers live there.
_PROJECT_ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_PROJECT_ENV):
    load_dotenv(_PROJECT_ENV, override=True)
load_dotenv(os.path.expanduser("~/.env"), override=False)
load_dotenv(os.path.expanduser("~/Documents/medbar/.env"), override=False)


class CloudLLMClient:
    """Unified client for cloud LLM APIs."""

    def __init__(self, provider: str, model: str = None):
        """
        Initialize cloud LLM client.

        Args:
            provider: One of 'openai', 'google', 'openrouter', 'xai', 'deepseek', 'kimi'
            model: Model name (defaults based on provider)
        """
        self.provider = provider.lower()
        self.usage_stats = {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0}

        # Set default models and API keys
        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4o"
            self.base_url = "https://api.openai.com/v1"
        elif self.provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            self.model = model or "gemini-2.0-flash"
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        elif self.provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.model = model or "anthropic/claude-sonnet-4"
            self.base_url = "https://openrouter.ai/api/v1"
        elif self.provider == "xai":
            # xAI's native API is OpenAI-compatible. Use this instead of routing
            # Grok through openrouter to avoid OpenRouter's model-deprecation
            # gating. Model names are xAI-native and use hyphens, not periods —
            # e.g. xAI's "grok-4-1-fast" == OpenRouter's "x-ai/grok-4.1-fast".
            self.api_key = os.getenv("XAI_API_KEY")
            self.model = model or "grok-4-1-fast"
            self.base_url = "https://api.x.ai/v1"
        elif self.provider == "deepseek":
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
            self.model = model or "deepseek-chat"  # V3.2-Exp
            self.base_url = "https://api.deepseek.com"
        elif self.provider == "kimi":
            self.api_key = os.getenv("MOONSHOT_API_KEY")
            self.model = model or "moonshot-v1-auto"  # Kimi K2.5
            self.base_url = "https://api.moonshot.cn/v1"
        elif self.provider == "huggingface":
            self.api_key = os.getenv("HF_TOKEN")
            self.model = model or "google/medgemma-27b-text-it"
            # base_url should be set to the dedicated endpoint URL
            self.base_url = os.getenv("HF_ENDPOINT_URL", "")
            if not self.base_url:
                raise ValueError("HF_ENDPOINT_URL must be set for huggingface provider")
        elif self.provider == "dr7":
            self.api_key = os.getenv("DR7AI_API")
            self.model = model or "medgemma-4b-it"
            self.base_url = "https://dr7.ai/api/v1/medical"
        else:
            raise ValueError(f"Unknown provider: {provider}")

        if not self.api_key:
            raise ValueError(f"No API key found for {provider}")

    def _safe_request(self, url: str, headers: dict, json: dict, timeout: int = 300) -> requests.Response:
        """Make an HTTP request with safe error handling that never leaks API keys."""
        try:
            response = requests.post(url, headers=headers, json=json, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            logger.error("LLM API error: provider=%s model=%s status=%s", self.provider, self.model, status)
            raise RuntimeError(
                f"LLM API request failed ({self.provider}/{self.model}): HTTP {status}"
            ) from None  # 'from None' suppresses the original traceback that may contain auth headers
        except requests.exceptions.Timeout:
            logger.error("LLM API timeout: provider=%s model=%s", self.provider, self.model)
            raise RuntimeError(
                f"LLM API request timed out ({self.provider}/{self.model}) after {timeout}s"
            ) from None
        except requests.exceptions.ConnectionError:
            logger.error("LLM API connection error: provider=%s model=%s", self.provider, self.model)
            raise RuntimeError(
                f"LLM API connection failed ({self.provider}/{self.model})"
            ) from None

    def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
        system_prompt: str = None,
        json_mode: bool = False
    ) -> str:
        """Generate text completion."""

        if self.provider == "openai":
            return self._openai_generate(prompt, max_tokens, temperature, system_prompt)
        elif self.provider == "google":
            return self._google_generate(prompt, max_tokens, temperature, system_prompt, json_mode=json_mode)
        elif self.provider == "openrouter":
            return self._openrouter_generate(prompt, max_tokens, temperature, system_prompt)
        elif self.provider == "xai":
            return self._xai_generate(prompt, max_tokens, temperature, system_prompt)
        elif self.provider == "deepseek":
            return self._deepseek_generate(prompt, max_tokens, temperature, system_prompt)
        elif self.provider == "kimi":
            return self._kimi_generate(prompt, max_tokens, temperature, system_prompt)
        elif self.provider == "huggingface":
            return self._huggingface_generate(prompt, max_tokens, temperature, system_prompt)
        elif self.provider == "dr7":
            return self._dr7_generate(prompt, max_tokens, temperature, system_prompt)

    def _openai_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None
    ) -> str:
        """OpenAI API call."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
        }
        # Newer OpenAI models (GPT-5.x and the o-series reasoning models) require
        # 'max_completion_tokens' and only accept the default temperature; older
        # models use 'max_tokens' + an explicit temperature.
        _m = (self.model or "").lower()
        if _m.startswith("gpt-5") or _m.startswith(("o1", "o3", "o4")):
            data["max_completion_tokens"] = max_tokens
        else:
            data["max_tokens"] = max_tokens
            data["temperature"] = temperature

        response = self._safe_request(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        result = response.json()

        # Track usage
        if "usage" in result:
            self.usage_stats["input_tokens"] += result["usage"].get("prompt_tokens", 0)
            self.usage_stats["output_tokens"] += result["usage"].get("completion_tokens", 0)

        return result["choices"][0]["message"]["content"]

    def _google_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None,
        json_mode: bool = False
    ) -> str:
        """Google Gemini API call."""
        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        # Build content with optional system instruction
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        generation_config = {
            "maxOutputTokens": max_tokens,
            "temperature": temperature
        }
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        data = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": generation_config
        }

        response = self._safe_request(url, headers=headers, json=data)
        result = response.json()

        # Track usage (Gemini reports in usageMetadata)
        if "usageMetadata" in result:
            self.usage_stats["input_tokens"] += result["usageMetadata"].get("promptTokenCount", 0)
            self.usage_stats["output_tokens"] += result["usageMetadata"].get("candidatesTokenCount", 0)

        return result["candidates"][0]["content"]["parts"][0]["text"]

    def _openrouter_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None
    ) -> str:
        """OpenRouter API call (same format as OpenAI)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://medbar.ai",
            "X-Title": "MedBAR Case Processing"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._safe_request(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        result = response.json()

        # Track usage
        if "usage" in result:
            self.usage_stats["input_tokens"] += result["usage"].get("prompt_tokens", 0)
            self.usage_stats["output_tokens"] += result["usage"].get("completion_tokens", 0)

        return result["choices"][0]["message"]["content"]

    def _xai_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None
    ) -> str:
        """xAI native API call (OpenAI-compatible, hits api.x.ai directly)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = self._safe_request(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        result = response.json()

        if "usage" in result:
            self.usage_stats["input_tokens"] += result["usage"].get("prompt_tokens", 0)
            self.usage_stats["output_tokens"] += result["usage"].get("completion_tokens", 0)

        return result["choices"][0]["message"]["content"]

    def _deepseek_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None
    ) -> str:
        """DeepSeek API call (OpenAI-compatible with automatic caching)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._safe_request(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        result = response.json()

        # Track usage - DeepSeek reports cache_read_input_tokens for cache hits
        if "usage" in result:
            usage = result["usage"]
            self.usage_stats["input_tokens"] += usage.get("prompt_tokens", 0)
            self.usage_stats["output_tokens"] += usage.get("completion_tokens", 0)
            # DeepSeek-specific: cache_read_input_tokens indicates cached token count
            self.usage_stats["cache_read_tokens"] += usage.get("prompt_cache_hit_tokens", 0)

        return result["choices"][0]["message"]["content"]

    def _kimi_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None
    ) -> str:
        """Kimi (Moonshot) API call (OpenAI-compatible)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._safe_request(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        result = response.json()

        # Track usage
        if "usage" in result:
            self.usage_stats["input_tokens"] += result["usage"].get("prompt_tokens", 0)
            self.usage_stats["output_tokens"] += result["usage"].get("completion_tokens", 0)

        return result["choices"][0]["message"]["content"]

    def _dr7_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None
    ) -> str:
        """Dr7.ai API call (OpenAI-compatible)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._safe_request(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        result = response.json()

        if "usage" in result:
            self.usage_stats["input_tokens"] += result["usage"].get("prompt_tokens", 0)
            self.usage_stats["output_tokens"] += result["usage"].get("completion_tokens", 0)

        return result["choices"][0]["message"]["content"]

    def _huggingface_generate(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str = None
    ) -> str:
        """HuggingFace Inference Endpoint (TGI) using /generate with Gemma chat template."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build Gemma 3 chat template
        formatted = ""
        if system_prompt:
            formatted += f"<start_of_turn>user\n{system_prompt}\n\n{prompt}<end_of_turn>\n"
        else:
            formatted += f"<start_of_turn>user\n{prompt}<end_of_turn>\n"
        formatted += "<start_of_turn>model\n"

        data = {
            "inputs": formatted,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "stop": ["<end_of_turn>", "<start_of_turn>"],
            },
        }

        response = self._safe_request(
            f"{self.base_url}/generate",
            headers=headers,
            json=data,
        )
        result = response.json()

        text = result.get("generated_text", "")
        # Clean up any trailing special tokens
        for token in ["<end_of_turn>", "<start_of_turn>"]:
            text = text.split(token)[0]
        return text.strip()

    def generate_with_images(
        self,
        prompt: str,
        image_paths: list,
        max_tokens: int = 4096,
        temperature: float = 0.1,
        system_prompt: str = None,
    ) -> str:
        """Generate text completion with images (multimodal).

        Args:
            prompt: Text prompt
            image_paths: List of image file paths to include
            max_tokens: Max output tokens
            temperature: Sampling temperature
            system_prompt: Optional system prompt

        Returns:
            Generated text response
        """
        # Read and encode images
        encoded_images = []
        for path in image_paths:
            path = Path(path)
            if not path.exists():
                logger.warning("Image not found, skipping: %s", path)
                continue
            ext = path.suffix.lower()
            mime_map = {
                ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
            }
            mime_type = mime_map.get(ext, "image/png")
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            encoded_images.append({"mime_type": mime_type, "data": data})

        if not encoded_images:
            logger.warning("No valid images found, falling back to text-only generate")
            return self.generate(prompt, max_tokens, temperature, system_prompt)

        if self.provider == "google":
            return self._google_generate_with_images(
                prompt, encoded_images, max_tokens, temperature, system_prompt
            )
        elif self.provider in ("openai", "openrouter", "xai"):
            return self._openai_generate_with_images(
                prompt, encoded_images, max_tokens, temperature, system_prompt
            )
        else:
            # Fallback: text-only for providers without multimodal support
            logger.warning("Provider %s does not support images, using text-only", self.provider)
            return self.generate(prompt, max_tokens, temperature, system_prompt)

    def _google_generate_with_images(
        self, prompt: str, encoded_images: list, max_tokens: int,
        temperature: float, system_prompt: str = None,
    ) -> str:
        """Google Gemini multimodal API call."""
        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        # Build multipart content: text + images
        parts = [{"text": full_prompt}]
        for img in encoded_images:
            parts.append({
                "inline_data": {
                    "mime_type": img["mime_type"],
                    "data": img["data"],
                }
            })

        data = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        response = self._safe_request(url, headers=headers, json=data)
        result = response.json()

        if "usageMetadata" in result:
            self.usage_stats["input_tokens"] += result["usageMetadata"].get("promptTokenCount", 0)
            self.usage_stats["output_tokens"] += result["usageMetadata"].get("candidatesTokenCount", 0)

        return result["candidates"][0]["content"]["parts"][0]["text"]

    def _openai_generate_with_images(
        self, prompt: str, encoded_images: list, max_tokens: int,
        temperature: float, system_prompt: str = None,
    ) -> str:
        """OpenAI/OpenRouter multimodal API call."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://medbar.ai"
            headers["X-Title"] = "MedBAR Case Processing"

        # Build content array with text + images
        content = [{"type": "text", "text": prompt}]
        for img in encoded_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['mime_type']};base64,{img['data']}",
                },
            })

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        url = f"{self.base_url}/chat/completions"
        response = self._safe_request(url, headers=headers, json=data)
        result = response.json()

        if "usage" in result:
            self.usage_stats["input_tokens"] += result["usage"].get("prompt_tokens", 0)
            self.usage_stats["output_tokens"] += result["usage"].get("completion_tokens", 0)

        return result["choices"][0]["message"]["content"]

    def get_cost_estimate(self) -> Dict[str, float]:
        """Estimate cost based on usage stats and provider pricing."""
        pricing = {
            "openai": {"input": 2.50, "output": 10.00},  # GPT-4o per 1M tokens
            "google": {"input": 0.075, "output": 0.30},  # Gemini 2.0 Flash
            "openrouter": {"input": 3.00, "output": 15.00},  # Claude Sonnet 4
            "xai": {"input": 0.20, "output": 0.50},  # Grok-4 Fast (non-reasoning) per 1M tokens
            "deepseek": {"input": 0.28, "output": 0.42, "cache": 0.028},  # V3.2-Exp
            "kimi": {"input": 0.50, "output": 2.80},  # Kimi K2.5
        }

        rates = pricing.get(self.provider, {"input": 1.0, "output": 1.0})

        # Calculate costs
        input_cost = (self.usage_stats["input_tokens"] / 1_000_000) * rates["input"]
        output_cost = (self.usage_stats["output_tokens"] / 1_000_000) * rates["output"]

        # DeepSeek cache savings
        cache_savings = 0
        if self.provider == "deepseek" and "cache" in rates:
            cache_tokens = self.usage_stats["cache_read_tokens"]
            cache_savings = (cache_tokens / 1_000_000) * (rates["input"] - rates["cache"])

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "cache_savings": cache_savings,
            "total_cost": input_cost + output_cost - cache_savings,
            "input_tokens": self.usage_stats["input_tokens"],
            "output_tokens": self.usage_stats["output_tokens"],
            "cache_read_tokens": self.usage_stats["cache_read_tokens"],
        }

    def extract_json(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Extract JSON from prompt response."""
        # Add JSON instruction
        full_prompt = prompt + "\n\nReturn ONLY valid JSON, no other text."

        response = self.generate(full_prompt, max_tokens=max_tokens)

        # Try to extract JSON from response
        try:
            # Try direct parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(response[start:end])
                except json.JSONDecodeError:
                    pass

            # Try array
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(response[start:end])
                except json.JSONDecodeError:
                    pass

        return {"error": "Failed to parse JSON", "raw": response[:500]}


def get_cloud_client(provider: str, model: str = None) -> CloudLLMClient:
    """Get a cloud LLM client."""
    return CloudLLMClient(provider=provider, model=model)


# Available models for comparison (2025/2026)
COMPARISON_MODELS = {
    # === BUDGET-FRIENDLY via OpenRouter ===
    "deepseek-v3": ("openrouter", "deepseek/deepseek-chat"),  # DeepSeek V3 - very cheap
    "deepseek-v3.2": ("openrouter", "deepseek/deepseek-v3.2"),  # Latest V3.2
    "deepseek-v3.2-exp": ("openrouter", "deepseek/deepseek-v3.2-exp"),  # Experimental

    # === BUDGET-FRIENDLY Direct API (if keys available) ===
    "deepseek-direct": ("deepseek", "deepseek-chat"),  # Direct API - cheaper with caching
    "kimi-k2": ("kimi", "moonshot-v1-128k"),  # Kimi K2.5

    # === GOOGLE (Good balance) ===
    "gemini-2.0-flash": ("google", "gemini-2.0-flash"),  # $0.075/1M
    "gemini-2.5-pro": ("google", "gemini-2.5-pro"),
    "gemini-2.5-flash": ("google", "gemini-2.5-flash"),

    # === PREMIUM (Baseline quality) ===
    "claude-sonnet-4": ("openrouter", "anthropic/claude-sonnet-4"),  # $3/1M in
    "gpt-4o": ("openai", "gpt-4o"),  # $2.50/1M in

    # === OTHER ===
    "gpt-5": ("openrouter", "openai/gpt-5"),
    "grok-4.1": ("openrouter", "x-ai/grok-4.1-fast"),
    "gpt-4.1": ("openai", "gpt-4.1"),
}

# Model pricing per 1M tokens (for cost estimation)
MODEL_PRICING = {
    "deepseek-v3": {"input": 0.28, "output": 0.42, "cache": 0.028},
    "kimi-k2": {"input": 0.50, "output": 2.80},
    "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


if __name__ == "__main__":
    import sys

    # Test specific providers or all
    test_models = sys.argv[1:] if len(sys.argv) > 1 else ["deepseek-v3", "kimi-k2", "gemini-2.0-flash"]

    test_prompt = "What is 2+2? Reply with just the number."

    for name in test_models:
        if name not in COMPARISON_MODELS:
            print(f"{name}: Unknown model")
            continue

        provider, model = COMPARISON_MODELS[name]
        try:
            client = get_cloud_client(provider, model)
            result = client.generate(test_prompt, max_tokens=10)
            print(f"{name}: {result.strip()}")
        except Exception as e:
            print(f"{name}: ERROR - {e}")
