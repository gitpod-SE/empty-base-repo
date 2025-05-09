from fastapi import APIRouter

from app.api.v1 import items

router = APIRouter()
router.include_router(items.router, prefix="/v1/items", tags=["Items"])
