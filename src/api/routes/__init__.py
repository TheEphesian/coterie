"""API routes package."""

from src.api.routes.characters import router as characters_router
from src.api.routes.players import router as players_router
from src.api.routes.apr import router as apr_router
from src.api.routes.imports import router as imports_router
from src.api.routes.boons import router as boons_router

__all__ = ["characters_router", "players_router", "apr_router", "imports_router", "boons_router"]
