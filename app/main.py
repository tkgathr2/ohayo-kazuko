"""FastAPIアプリケーション エントリーポイント"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI

# .envファイルをロード
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

from app.config import ensure_required_env, get_settings
from app.handlers import webhook_router
from app.schedulers import start_scheduler
from app.services import LineService, NotificationService, PhoneService, SpreadsheetService, TwilioService
from app.services.procast_service import ProcastService
from app.utils.logger import configure_logging


def create_app() -> FastAPI:
    """アプリケーションを作成"""
    try:
        ensure_required_env()
    except RuntimeError as e:
        import logging
        logging.warning("Some required env vars are missing: %s", e)
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_file)

    app = FastAPI(title="おはよう和子さん")

    scheduler = AsyncIOScheduler(timezone=settings.tz)
    sheet_service = SpreadsheetService(settings)
    line_service = LineService(settings)
    twilio_service = TwilioService(settings)
    procast_service = ProcastService(settings)
    notification_service = NotificationService(settings, line_service, sheet_service)
    phone_service = PhoneService(scheduler, twilio_service, sheet_service, notification_service)

    app.state.scheduler = scheduler
    app.state.sheet_service = sheet_service
    app.state.line_service = line_service
    app.state.twilio_service = twilio_service
    app.state.phone_service = phone_service
    app.state.notification_service = notification_service
    app.state.procast_service = procast_service
    app.state.settings = settings

    # ベースパスを設定（他システムとの衝突を避けるため一意のパスを使用）
    api_prefix = "/api/ohayo-kazuko/v1"
    app.include_router(webhook_router, prefix=api_prefix)

    @app.on_event("startup")
    async def startup_event() -> None:
        start_scheduler(
            scheduler,
            notification_service,
            phone_service,
            sheet_service,
            procast_service,
            settings,
        )

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        try:
            scheduler.shutdown(wait=True)
        except Exception:
            pass
        await line_service.close()
        await twilio_service.close()

    @app.get(f"{api_prefix}/health")
    async def health() -> dict:
        now = datetime.now(ZoneInfo(settings.tz))
        return {"status": "healthy", "timestamp": now.isoformat()}

    return app


app = create_app()
