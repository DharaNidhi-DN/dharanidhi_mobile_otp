import logging
import time
from uuid import uuid4
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from mobile_otp.api.routers.otp import router as otp_router
from mobile_otp.core.config import get_settings
from mobile_otp.core.logging import request_id_ctx, setup_logging, shutdown_logging
from mobile_otp.db.init_db import init_db
from mobile_otp.db.session import SessionLocal
from mobile_otp.integrations.twilio_verify_client import TwilioVerifyClient
from mobile_otp.services.otp_service import OtpService

logger = logging.getLogger(__name__)
request_logger = logging.getLogger("mobile_otp.request")
health_logger = logging.getLogger("mobile_otp.health")


def _log_db_target(database_url: str) -> None:
    logger = logging.getLogger("mobile_otp")
    parsed = urlparse(database_url)
    host = parsed.hostname or "unknown"
    port = parsed.port or 5432
    logger.info("Database target: %s:%s", host, port)


def create_app() -> FastAPI:
    settings = get_settings()
    logging_handle = setup_logging(settings)
    logger.info(
        "logging_initialized",
        extra={"log_level": settings.log_level, "log_json": settings.log_json}
    )
    _log_db_target(settings.database_url)
    client = TwilioVerifyClient(
        account_sid=settings.twilio_account_sid,
        auth_token=settings.twilio_auth_token,
        service_sid=settings.twilio_service_sid,
        base_url=settings.twilio_base_url
    )
    otp_service = OtpService(client=client, settings=settings, session_factory=SessionLocal)

    app = FastAPI(title="Mobile OTP API")
    app.state.logging_handle = logging_handle
    app.state.settings = settings
    app.state.otp_service = otp_service

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        token = request_id_ctx.set(request_id)
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        except Exception:
            request_logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else None,
                },
            )
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            status_code = response.status_code if response else 500
            request_logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            if response is not None:
                response.headers["X-Request-ID"] = request_id
            request_id_ctx.reset(token)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_private_network=settings.cors_allow_private_network
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("app_startup")
        await init_db()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("app_shutdown")
        await client.close()
        shutdown_logging(app.state.logging_handle)

    @app.get("/health")
    def health_check() -> dict[str, str]:
        health_logger.info("health_check")
        return {"status": "ok"}

    app.include_router(otp_router)
    return app


app = create_app()


def main() -> None:
    import uvicorn

    settings = app.state.settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_config=None,
        log_level=settings.log_level.lower(),
        access_log=False,
    )


if __name__ == "__main__":
    main()
