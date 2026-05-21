import json
import socket
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from backend.services.settings import get_setting


class LLMServiceError(RuntimeError):
    pass


class QwenLLMService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 45,
    ):
        self.provider = get_setting("LLM_PROVIDER", "qwen")
        self.api_key = api_key or self._configured_api_key()
        self.base_url = (base_url or self._configured_base_url()).rstrip("/")
        self.model = model or self._configured_model()
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def chat_json(self, system_prompt: str, user_prompt: str) -> Any:
        content = self.chat(system_prompt, user_prompt, response_format={"type": "json_object"})
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(content[start : end + 1])
                except json.JSONDecodeError:
                    pass
            raise LLMServiceError("LLM did not return valid JSON.") from exc

    def chat(self, system_prompt: str, user_prompt: str, response_format: Optional[Dict[str, str]] = None) -> str:
        if not self.api_key:
            raise LLMServiceError("LLM API key is not configured.")
        if self.provider == "anthropic":
            return self._chat_anthropic(system_prompt, user_prompt)

        return self._chat_openai_compatible(system_prompt, user_prompt, response_format)

    def _configured_api_key(self) -> str:
        if self.provider == "qwen":
            return get_setting("DASHSCOPE_API_KEY") or get_setting("LLM_API_KEY")
        if self.provider == "openai":
            return get_setting("OPENAI_API_KEY") or get_setting("LLM_API_KEY")
        if self.provider == "anthropic":
            return get_setting("ANTHROPIC_API_KEY") or get_setting("LLM_API_KEY")
        return get_setting("LLM_API_KEY")

    def _configured_base_url(self) -> str:
        if get_setting("LLM_BASE_URL"):
            return get_setting("LLM_BASE_URL")
        if self.provider == "openai":
            return "https://api.openai.com/v1"
        if self.provider == "anthropic":
            return "https://api.anthropic.com"
        return get_setting("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    def _configured_model(self) -> str:
        if get_setting("LLM_MODEL"):
            return get_setting("LLM_MODEL")
        if self.provider == "openai":
            return "gpt-4.1-mini"
        if self.provider == "anthropic":
            return "claude-3-5-sonnet-latest"
        return get_setting("QWEN_MODEL", "qwen-plus")

    def _chat_openai_compatible(self, system_prompt: str, user_prompt: str, response_format: Optional[Dict[str, str]] = None) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        if response_format:
            payload["response_format"] = response_format

        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise LLMServiceError(f"Qwen API HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LLMServiceError(f"Qwen API request failed: {exc}") from exc
        except socket.timeout as exc:
            raise LLMServiceError("Qwen API request timed out.") from exc

        choices: List[Dict[str, Any]] = data.get("choices", [])
        if not choices:
            raise LLMServiceError("LLM API returned no choices.")
        return choices[0]["message"]["content"]

    def _chat_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": 1600,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        request = urllib.request.Request(
            f"{self.base_url}/v1/messages",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise LLMServiceError(f"Anthropic API HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LLMServiceError(f"Anthropic API request failed: {exc}") from exc
        except socket.timeout as exc:
            raise LLMServiceError("Anthropic API request timed out.") from exc

        blocks = data.get("content", [])
        texts = [block.get("text", "") for block in blocks if block.get("type") == "text"]
        if not texts:
            raise LLMServiceError("Anthropic API returned no text.")
        return "\n".join(texts)
