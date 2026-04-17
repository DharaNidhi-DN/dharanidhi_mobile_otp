import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status

from mobile_otp.api.schemas.otp import (
    SendOtpRequest,
    SendOtpResponse,
    VerifyOtpRequest,
    VerifyOtpResponse
)
from mobile_otp.core.errors import OtpExpiredError, OtpRequestNotFoundError
from mobile_otp.services.otp_service import OtpService
from mobile_otp.utils.redaction import mask_phone

router = APIRouter(prefix="/otp", tags=["otp"])
logger = logging.getLogger(__name__)


def get_otp_service(request: Request) -> OtpService:
    return request.app.state.otp_service


@router.post("/send", response_model=SendOtpResponse)
async def send_otp(
    payload: SendOtpRequest,
    service: OtpService = Depends(get_otp_service)
) -> SendOtpResponse:
    try:
        logger.info(
            "api_send_otp",
            extra={"phone": mask_phone(payload.phone_number), "channel": payload.channel}
        )
        otp_request = await service.send_otp(payload.phone_number, payload.channel)
    except httpx.HTTPStatusError as exc:
        detail = "Twilio verification request failed"
        try:
            error_data = exc.response.json()
            error_message = error_data.get("message")
            error_code = error_data.get("code")
            if error_message:
                detail = error_message
            logger.warning(
                "api_send_otp_failed",
                extra={
                    "error": exc.__class__.__name__,
                    "status_code": exc.response.status_code,
                    "twilio_code": error_code,
                    "twilio_message": error_message
                }
            )
        except Exception as e:
            logger.warning(
                "api_send_otp_failed",
                extra={
                    "error": exc.__class__.__name__,
                    "status_code": exc.response.status_code,
                    "parse_error": str(e)
                }
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning(
            "api_send_otp_failed",
            extra={"error": exc.__class__.__name__}
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Twilio verification request failed"
        ) from exc

    logger.info(
        "api_send_otp_success",
        extra={"request_id": otp_request.id, "status": otp_request.status.value}
    )
    return SendOtpResponse(
        request_id=otp_request.id,
        status=otp_request.status.value,
        twilio_sid=otp_request.twilio_verification_sid,
        channel=otp_request.channel,
        to=otp_request.phone_number,
        created_at=otp_request.created_at,
        expires_at=otp_request.expires_at
    )


@router.post("/verify", response_model=VerifyOtpResponse)
async def verify_otp(
    payload: VerifyOtpRequest,
    service: OtpService = Depends(get_otp_service)
) -> VerifyOtpResponse:
    try:
        logger.info(
            "api_verify_otp",
            extra={"phone": mask_phone(payload.phone_number)}
        )
        otp_request, response = await service.verify_otp(payload.phone_number, payload.code)
    except OtpRequestNotFoundError as exc:
        logger.warning("api_verify_missing_request", extra={"detail": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
    except OtpExpiredError as exc:
        logger.info("api_verify_expired", extra={"detail": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(exc)
        ) from exc
    except httpx.HTTPStatusError as exc:
        detail = "Twilio verification check failed"
        try:
            error_data = exc.response.json()
            error_message = error_data.get("message")
            error_code = error_data.get("code")
            if error_message:
                detail = error_message
            logger.warning(
                "api_verify_twilio_failed",
                extra={
                    "error": exc.__class__.__name__,
                    "status_code": exc.response.status_code,
                    "twilio_code": error_code,
                    "twilio_message": error_message
                }
            )
        except Exception as e:
            logger.warning(
                "api_verify_twilio_failed",
                extra={
                    "error": exc.__class__.__name__,
                    "status_code": exc.response.status_code,
                    "parse_error": str(e)
                }
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning(
            "api_verify_twilio_failed",
            extra={"error": exc.__class__.__name__}
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Twilio verification check failed"
        ) from exc

    logger.info(
        "api_verify_success",
        extra={"request_id": otp_request.id, "status": otp_request.status.value}
    )
    return VerifyOtpResponse(
        request_id=otp_request.id,
        status=otp_request.status.value,
        valid=response.get("valid", False) is True,
        twilio_status=response.get("status"),
        verified_at=datetime.now(timezone.utc)
    )
