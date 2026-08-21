from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    """Allows access only to superuser admins."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='SUPER_ADMIN').exists()))


class IsTimetableAdmin(BasePermission):
    """Allows access to timetable coordinators and superusers."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        return request.user.groups.filter(name__in=['SUPER_ADMIN', 'TIMETABLE_ADMIN']).exists()


class IsFacultyUser(BasePermission):
    """Allows access to faculty members and staff."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(request.user.is_staff or request.user.groups.filter(name__in=['SUPER_ADMIN', 'TIMETABLE_ADMIN', 'FACULTY']).exists())


class IsAdminOrReadOnly(BasePermission):
    """Allows read access to anyone or view_only role, write access to timetable admins."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))
