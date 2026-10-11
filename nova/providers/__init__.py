from ..config import Settings
from .base import ChatProvider


def create_provider(settings: Settings) -> ChatProvider:
    if settings.provider == "local":
        from .local import LocalProvider

        return LocalProvider(settings)
    raise ValueError(f"Unknown provider: {settings.provider}")