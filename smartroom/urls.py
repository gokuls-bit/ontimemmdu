from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.api.urls')),
    path('timetable-legacy/', include('timetable.urls')),

    # Serve static assets directly for frontend bundle
    re_path(r'^assets/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'static', 'frontend', 'assets'),
    }),
    re_path(r'^static/frontend/assets/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'static', 'frontend', 'assets'),
    }),

    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
