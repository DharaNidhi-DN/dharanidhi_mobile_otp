from __future__ import annotations

import json
import logging
import logging.handlers
import queue
import sys
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from mobile_otp.core.config import Settings

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
logger = logging.getLogger(__name__)

_STANDARD_RECORD_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
    "request_id",
}


@dataclass
class LoggingListener:
    listener: logging.handlers.QueueListener


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or "-"
        return True


class JsonFormatter(logging.Formatter):
    def __init__(self, *, service: str, app_env: str) -> None:
        super().__init__()
        self._service = service
        self._app_env = app_env

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc)
        payload: dict[str, Any] = {
            "timestamp": timestamp.isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self._service,
            "env": self._app_env,
            "request_id": getattr(record, "request_id", "-"),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_RECORD_ATTRS
        }
        if extras:
            payload.update(extras)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def setup_logging(settings: Settings) -> LoggingListener:
    log_level = settings.log_level.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    log_queue: queue.SimpleQueue[logging.LogRecord] = queue.SimpleQueue()
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.setLevel(log_level)
    queue_handler.addFilter(RequestIdFilter())

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    if settings.log_json:
        formatter: logging.Formatter = JsonFormatter(
            service="mobile_otp",
            app_env=settings.app_env
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(RequestIdFilter())

    listener = logging.handlers.QueueListener(
        log_queue,
        stream_handler,
        respect_handler_level=True
    )
    listener.start()
    root_logger.addHandler(queue_handler)

    app_logger = logging.getLogger("mobile_otp")
    app_logger.setLevel(log_level)
    app_logger.handlers = [queue_handler]
    app_logger.propagate = False
    app_logger.disabled = False

    main_logger = logging.getLogger("__main__")
    main_logger.setLevel(log_level)
    main_logger.handlers = [queue_handler]
    main_logger.propagate = False
    main_logger.disabled = False

    for name, logger_obj in logging.root.manager.loggerDict.items():
        if isinstance(logger_obj, logging.Logger) and name.startswith("mobile_otp"):
            logger_obj.disabled = False
            logger_obj.setLevel(log_level)
            logger_obj.handlers = [queue_handler]
            logger_obj.propagate = False

    for noisy in ("uvicorn", "uvicorn.error", "uvicorn.access", "asyncio"):
        logger = logging.getLogger(noisy)
        logger.handlers = []
        logger.propagate = True
        logger.setLevel(log_level)

    logging.getLogger("sqlalchemy.engine").setLevel("WARNING")

    return LoggingListener(listener=listener)


def shutdown_logging(handle: LoggingListener | None) -> None:
    if handle:
        handle.listener.stop()


logger.debug("logging_module_loaded")
