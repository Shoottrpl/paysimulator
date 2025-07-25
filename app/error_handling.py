import uuid
from typing import Dict, List

import sentry_sdk
from pydantic import ValidationError
from sanic.exceptions import Forbidden, NotFound, Unauthorized
from sanic.request import Request
from sanic.response import HTTPResponse, json

from app.logger import LOGS


def format_validation_errors(errors: List[Dict]) -> List[Dict]:
    return [
        {
            "field": ".".join(map(str, error["loc"])),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in errors
    ]


def generate_error_id() -> str:
    return str(uuid.uuid4())


async def global_error_handler(request: Request, exception: Exception) -> HTTPResponse:
    error_id = None

    try:
        if isinstance(exception, ValidationError):
            return json(
                {
                    "error": "Validation Error",
                    "details": format_validation_errors(exception.errors()),
                }
            )

        if isinstance(exception, Unauthorized):
            return json({"error": "Authorization required"}, status=401)

        if isinstance(exception, NotFound):
            return json({"error": "Resource not found"}, status=404)

        if isinstance(exception, Forbidden):
            return json({"error": "Access denied"}, status=403)

        error_id = generate_error_id()
        LOGS.error(f"Unhandled exception [{error_id}]", exc_info=exception)

        with sentry_sdk.new_scope() as scope:
            scope.set_tag("error_id", error_id)
            scope.set_context(
                "request",
                {
                    "method": request.method,
                    "path": request.path,
                    "query": request.query_string,
                    "ip": request.ip,
                },
            )
            sentry_sdk.capture_exception(exception)

        return json(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
                "error_id": error_id,
            },
            status=500,
        )

    except Exception as inner_ex:
        error_id = error_id or generate_error_id()

        LOGS.error(
            f"CRITICAL: Error in error handler [{error_id}]: {str(inner_ex)}",
            exc_info=True,
        )

        sentry_sdk.capture_exception(inner_ex)

        return json(
            {
                "error": "Critical System Failure",
                "error_id": error_id,
                "message": "An error occurred while processing another error",
            },
            status=500,
        )
