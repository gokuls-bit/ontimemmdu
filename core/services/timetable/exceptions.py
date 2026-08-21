class TimetableDecisionEngineError(Exception):
    """Base exception for CSE SmartRoom decision engine."""
    pass


class InvalidStudentContext(TimetableDecisionEngineError):
    """Raised when the specified semester, section, or group combination is invalid."""
    pass


class InvalidSemester(TimetableDecisionEngineError):
    """Raised when the semester identifier does not exist or is inactive."""
    pass


class InvalidSection(TimetableDecisionEngineError):
    """Raised when the section name does not exist for the semester."""
    pass


class InvalidGroup(TimetableDecisionEngineError):
    """Raised when the group does not exist for the section."""
    pass


class NoTimetableFound(TimetableDecisionEngineError):
    """Raised when no timetable entries exist for the valid student context."""
    pass


class InvalidPeriodConfiguration(TimetableDecisionEngineError):
    """Raised when period configuration data is corrupted or invalid."""
    pass


class InvalidAcademicDate(TimetableDecisionEngineError):
    """Raised when an invalid date object or parameter is passed."""
    pass
