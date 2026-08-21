class LocationEngineError(Exception):
    """Base exception for CSE SmartRoom location intelligence engine."""
    pass


class RoomNotFound(LocationEngineError):
    """Raised when a room number or identifier is not found in the database."""
    pass


class TeacherNotFound(LocationEngineError):
    """Raised when a teacher name or employee ID is not found in the database."""
    pass


class InvalidLocationQuery(LocationEngineError):
    """Raised when search or filter query parameters are malformed."""
    pass


class ScheduleConflictError(LocationEngineError):
    """Base exception for location schedule conflict errors."""
    pass


class RoomScheduleConflict(ScheduleConflictError):
    """Raised when multiple non-merged timetable entries claim the same room at the same time."""
    pass


class TeacherScheduleConflict(ScheduleConflictError):
    """Raised when a teacher is assigned to multiple classes at the same time in different rooms."""
    pass
