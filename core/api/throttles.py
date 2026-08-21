from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class StudentAnonRateThrottle(AnonRateThrottle):
    """Rate limit for anonymous student API requests (e.g. 100/min)."""
    scope = 'student_anon'
    rate = '100/minute'


class StudentUserRateThrottle(UserRateThrottle):
    """Rate limit for authenticated user API requests (e.g. 300/min)."""
    scope = 'student_user'
    rate = '300/minute'
