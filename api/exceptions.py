from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse


class MyExceptionFormatter(ExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        error = error_response.errors[0]
        if (
            error_response.type == "validation_error"
            and error.attr != "non_field_errors"
            and error.attr is not None
        ):
            error_message = f"{error.attr}: {error.detail}"
        else:
            error_message = error.detail
        return {
            "success": False,
            "type": error_response.type,
            "code": error.code,
            "error": error_message,
        }
