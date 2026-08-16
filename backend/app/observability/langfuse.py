from contextlib import contextmanager
from typing import Any, Dict, Optional

from langfuse import get_client

from Config.Config import settings


def langfuse_enabled() -> bool:
    return bool(
        settings.langfuse_public_key
        and settings.langfuse_secret_key
    )


def get_langfuse_client():
    if not langfuse_enabled():
        return None

    try:
        return get_client()
    except Exception:
        return None


@contextmanager
def trace_request(
    name: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    client = get_langfuse_client()

    if client is None:
        yield None
        return

    try:
        with client.start_as_current_observation(
            name=name,
            metadata=metadata or {},
        ) as observation:
            yield observation
    except Exception:
        # Observability must never break the application.
        yield None
