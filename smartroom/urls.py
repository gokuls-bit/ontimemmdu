from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.api.urls')),
    path('timetable-legacy/', include('timetable.urls')),
    path('', include('core.urls')),
]

