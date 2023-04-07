from fastapi.routing import APIRouter
from starlette.routing import WebSocketRoute

from app.web.api import docs, monitoring, autonomous_agents

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(autonomous_agents.router)
