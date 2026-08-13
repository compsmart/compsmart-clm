"""Local persistence for anonymous preview session credentials."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile


def default_session_file() -> Path:
    """Return a per-user state path without placing credentials in the repository."""
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "Compsmart" / "CLM" / "sessions.json"
    if os.environ.get("XDG_STATE_HOME"):
        return Path(os.environ["XDG_STATE_HOME"]) / "compsmart-clm" / "sessions.json"
    return Path.home() / ".compsmart-clm" / "sessions.json"


def _key(base_url: str) -> str:
    return base_url.rstrip("/")


def _read_store(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"version": 1, "sessions": {}}
    if not isinstance(payload, dict) or not isinstance(payload.get("sessions"), dict):
        return {"version": 1, "sessions": {}}
    return payload


def _is_expired(expires_at: str) -> bool:
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return True
    if expiry.tzinfo is None:
        return True
    return expiry <= datetime.now(timezone.utc)


def load_session(path: Path, base_url: str) -> dict | None:
    session = _read_store(path)["sessions"].get(_key(base_url))
    if not isinstance(session, dict):
        return None
    token = session.get("token")
    expires_at = session.get("expires_at")
    if not isinstance(token, str) or not token or not isinstance(expires_at, str):
        return None
    if _is_expired(expires_at):
        return None
    return {"token": token, "expires_at": expires_at}


def save_session(path: Path, base_url: str, session: dict) -> None:
    token = session.get("token")
    expires_at = session.get("expires_at")
    if not isinstance(token, str) or not token or not isinstance(expires_at, str):
        raise ValueError("session response did not contain a token and expiry")

    payload = _read_store(path)
    payload["version"] = 1
    payload["sessions"][_key(base_url)] = {"token": token, "expires_at": expires_at}
    _write_store(path, payload)


def forget_session(path: Path, base_url: str) -> None:
    payload = _read_store(path)
    payload["sessions"].pop(_key(base_url), None)
    if payload["sessions"]:
        _write_store(path, payload)
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _write_store(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=path.name, delete=False
        ) as temporary:
            temporary_name = temporary.name
            json.dump(payload, temporary, indent=2)
            temporary.write("\n")
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass
