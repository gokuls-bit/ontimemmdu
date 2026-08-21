import os
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse, FileResponse, Http404, HttpResponseNotFound, HttpResponseBadRequest
from django.views import View
from .services.timetable.downloads import get_whitelisted_file_path


def student_app_view(request):
    """
    Serves the compiled React Module 6 Student Application SPA.
    """
    index_path = os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except Exception:
        return HttpResponse("<h1>CSE SmartRoom Student App</h1><p>Frontend static assets unavailable.</p>")


def download_timetable_view(request, semester: str, fmt: str):
    """
    Secure download view for 3rd, 4th, and 5th semester timetables (Excel or JSON).
    Strictly uses server-side whitelisting to prevent path traversal.
    """
    clean_sem = str(semester).strip().lower()
    clean_fmt = str(fmt).strip().lower()

    if clean_sem not in {'3rd', '4th', '5th'}:
        return HttpResponseBadRequest("Invalid semester specified. Supported: 3rd, 4th, 5th.")

    if clean_fmt not in {'excel', 'json'}:
        return HttpResponseBadRequest("Invalid format specified. Supported: excel, json.")

    file_path, content_type, err_code = get_whitelisted_file_path(clean_sem, clean_fmt)
    if not file_path or err_code:
        if err_code == "UNREGISTERED_FILE":
            return HttpResponseBadRequest("Requested file resource is not registered.")
        raise Http404("The requested timetable file is currently unavailable.")

    if clean_fmt == 'json':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Return sanitized normalized representation
            response_payload = {
                "semester": f"{clean_sem.capitalize()} Semester",
                "academic_year": "2026-27",
                "dataset": data
            }
            return JsonResponse(response_payload, json_dumps_params={'indent': 2})
        except Exception:
            return HttpResponse("Error reading timetable JSON data.", status=500)

    else:
        # Excel binary file download
        try:
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{clean_sem}_CSE_TimeTable.xlsx"'
            return response
        except Exception:
            return HttpResponseNotFound("Excel file unavailable on server.")
