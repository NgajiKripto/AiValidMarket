import json
import re
from openai import OpenAI
from app.utils.logger import info, error


class LLMClient:
    """Wrapper around OpenAI SDK following MiroFish pattern."""

    def __init__(self, api_key, base_url=None, model="gpt-4o-mini"):
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        info(f"LLMClient initialized with model: {model}")

    def chat(self, messages, temperature=0.7, max_tokens=4096, response_format=None):
        """Send a chat completion request and return the response text."""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            # Strip <think> tags (for models that include reasoning)
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
            content = content.strip()

            return content
        except Exception as e:
            error(f"LLM chat error: {e}")
            raise

    def chat_json(self, messages, temperature=0.7, max_tokens=4096):
        """Send a chat completion request and return parsed JSON dict."""
        content = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        # Clean up markdown code blocks if present
        content = re.sub(r"^```(?:json)?\s*\n?", "", content)
        content = re.sub(r"\n?```\s*$", "", content)
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            error(f"Failed to parse LLM JSON response: {e}")
            error(f"Raw content: {content[:500]}")
            raise
