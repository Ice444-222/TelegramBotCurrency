__all__ = ("router", )

from aiogram import Router

from .commands import router as commands_router
from .calculations import router as calculate_router
from .dates import router as dates_router

router = Router(name=__name__)

router.include_router(commands_router)
router.include_router(calculate_router)
router.include_router(dates_router)