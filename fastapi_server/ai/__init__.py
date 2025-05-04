from fastapi import APIRouter
from .gpt4o import router as gpt4o

router = APIRouter()
router.include_router(gpt4o)
