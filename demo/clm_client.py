"""Minimal standard-library client for the public Compsmart CLM preview."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://clm.compsmart.cloud"


class CLMError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class CLMClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 70.0,
        token: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token = token

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "User-Agent": "Compsmart-CLM-Client/0.1 (+https://github.com/compsmart/compsmart-clm)",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            self.base_url + path, data=body, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            try:
                detail = json.load(error).get("error", "request rejected")
            except Exception:
                detail = "request rejected"
            raise CLMError(f"HTTP {error.code}: {detail}", status_code=error.code) from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise CLMError(f"service unavailable: {error}") from error
        if not isinstance(result, dict):
            raise CLMError("invalid service response")
        return result

    def health(self) -> dict:
        return self._request("GET", "/v1/health")

    def create_session(self) -> dict:
        result = self._request("POST", "/v1/sessions", {})
        token = result.get("token")
        if not isinstance(token, str) or not token:
            raise CLMError("service did not issue a session token")
        self.token = token
        return result

    def chat(self, message: str) -> dict:
        if self.token is None:
            self.create_session()
        return self._request("POST", "/v1/chat", {"message": message})

    def delete_session(self) -> dict:
        if self.token is None:
            return {"deleted": False}
        try:
            return self._request("DELETE", "/v1/sessions/current")
        finally:
            self.token = None
