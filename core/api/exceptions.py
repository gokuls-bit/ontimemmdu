from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from core.services.timetable.exceptions import (
    TimetableDecisionEngineError, InvalidStudentContext, InvalidSemester,
    InvalidSection, InvalidGroup, NoTimetableFound, InvalidAcademicDate
)
from core.services.location.exceptions import (
    LocationEngineError, RoomNotFound, TeacherNotFound, InvalidLocationQuery,
    RoomScheduleConflict, TeacherScheduleConflict
)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler converting domain exceptions and DRF errors
    into structured JSON responses:
    {"success": false, "error": {"code": "ERROR_CODE", "message": "Safe human message"}}
    """
    response = exception_handler(exc, context)

    # 1. Handle Domain Exceptions from Module 3 (Timetable Engine)
    if isinstance(exc, (InvalidStudentContext, InvalidSemester, InvalidSection, InvalidGroup, InvalidAcademicDate)):
        return Response({
            "success": False,
            "error": {
                "code": exc.__class__.__name__.upper(),
                "message": str(exc)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, NoTimetableFound):
        return Response({
            "success": False,
            "error": {
                "code": "NO_TIMETABLE_FOUND",
                "message": str(exc)
            }
        }, status=status.HTTP_404_NOT_FOUND)

    # 2. Handle Domain Exceptions from Module 4 (Location Engine)
    if isinstance(exc, (RoomNotFound, TeacherNotFound)):
        return Response({
            "success": False,
            "error": {
                "code": exc.__class__.__name__.upper(),
                "message": str(exc)
            }
        }, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, InvalidLocationQuery):
        return Response({
            "success": False,
            "error": {
                "code": "INVALID_QUERY_PARAMETERS",
                "message": str(exc)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, (RoomScheduleConflict, TeacherScheduleConflict)):
        return Response({
            "success": False,
            "error": {
                "code": exc.__class__.__name__.upper(),
                "message": str(exc)
            }
        }, status=status.HTTP_409_CONFLICT)

    # 3. Handle DRF Exceptions (Validation Errors, Throttling, 404, 405, 500)
    if response is not None:
        err_code = "VALIDATION_ERROR" if response.status_code == 400 else "API_ERROR"
        if response.status_code == 429:
            err_code = "RATE_LIMIT_EXCEEDED"
        elif response.status_code == 404:
            err_code = "NOT_FOUND"

        err_msg = "A validation or request error occurred."
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                err_msg = str(response.data['detail'])
            else:
                # Format serializer errors cleanly
                err_msg = "; ".join([f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in response.data.items()])
        elif isinstance(response.data, str):
            err_msg = response.data

        response.data = {
            "success": False,
            "error": {
                "code": err_code,
                "message": err_msg
            }
        }
        return response

    # 4. Handle Unhandled Internal Server Errors (Hide Stack Trace)
    return Response({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred. Please try again later."
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
