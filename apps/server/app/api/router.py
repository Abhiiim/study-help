from fastapi import APIRouter

from app.api.routers import auth, collections, health, resources, tags

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(resources.router)
api_router.include_router(collections.router)
api_router.include_router(tags.router)
