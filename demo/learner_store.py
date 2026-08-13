"""Local persistence for an anonymous learner credential."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile


def default_learner_file() -> Path:
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
        return {"version": 2, "learners": {}}
    if not isinstance(payload, dict):
        return {"version": 2, "learners": {}}
    return payload


def _is_expired(expires_at: str) -> bool:
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return True
    return expiry.tzinfo is None or expiry <= datetime.now(timezone.utc)


def load_learner(path: Path, base_url: str) -> dict | None:
    payload = _read_store(path)
    learners = payload.get("learners", {})
    learner = learners.get(_key(base_url)) if isinstance(learners, dict) else None
    if (
        isinstance(learner, dict)
        and isinstance(learner.get("token"), str)
        and learner["token"]
    ):
        return {"learner_token": learner["token"]}

    # Migrate the session credential written by chat.py versions before v0.2.
    sessions = payload.get("sessions", {})
    session = sessions.get(_key(base_url)) if isinstance(sessions, dict) else None
    if not isinstance(session, dict):
        return None
    token = session.get("token")
    expires_at = session.get("expires_at")
    if not isinstance(token, str) or not token or not isinstance(expires_at, str):
        return None
    if _is_expired(expires_at):
        return None
    return {"source_session_token": token}


def save_learner(path: Path, base_url: str, token: str) -> None:
    if not token:
        raise ValueError("session response did not contain a learner token")
    payload = _read_store(path)
    learners = payload.get("learners")
    if not isinstance(learners, dict):
        learners = {}
    learners[_key(base_url)] = {"token": token}
    _write_store(path, {"version": 2, "learners": learners})


def forget_learner(path: Path, base_url: str) -> None:
    payload = _read_store(path)
    learners = payload.get("learners", {})
    if isinstance(learners, dict):
        learners.pop(_key(base_url), None)
    if learners:
        _write_store(path, {"version": 2, "learners": learners})
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
