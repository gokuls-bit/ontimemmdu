from django.urls import path
from .views import download_timetable_view, student_app_view

urlpatterns = [
    path('timetable/download/<str:semester>/<str:fmt>/', download_timetable_view, name='download_timetable'),
    path('', student_app_view, name='student_app'),
]
