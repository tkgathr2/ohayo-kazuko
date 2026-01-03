from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.config import ensure_required_env, get_settings
from app.handlers import webhook_router
from app.schedulers import start_scheduler
from app.services import LineService, NotificationService, PhoneService, SpreadsheetService, TwilioService
from app.utils.logger import configure_logging


def create_app() -> FastAPI:
    ensure_required_env()
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_file)

    app = FastAPI(title="kazuko_departure_watch")

    scheduler = AsyncIOScheduler(timezone=settings.tz)
    sheet_service = SpreadsheetService(settings)
    line_service = LineService(settings)
    twilio_service = TwilioService(settings)
    notification_service = NotificationService(settings, line_service, sheet_service)
    phone_service = PhoneService(scheduler, twilio_service, sheet_service, notification_service)

    app.state.scheduler = scheduler
    app.state.sheet_service = sheet_service
    app.state.line_service = line_service
    app.state.twilio_service = twilio_service
    app.state.phone_service = phone_service
    app.state.notification_service = notification_service

    app.include_router(webhook_router)

    @app.on_event("startup")
    async def startup_event() -> None:
        start_scheduler(scheduler, notification_service, phone_service, sheet_service)

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        scheduler.shutdown(wait=False)
        await line_service.close()
        await twilio_service.close()

    @app.get("/health")
    async def health() -> dict:
        now = datetime.now(ZoneInfo(settings.tz))
        return {"status": "healthy", "timestamp": now.isoformat()}

    return app


app = create_app()
