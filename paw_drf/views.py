from django.http import HttpResponse
import os
from django.conf import settings

def health_check(request):
    return HttpResponse("OK")

def test_view(request, path):
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(full_path):
        return HttpResponse(f"File exists: {full_path}")
    else:
        return HttpResponse(f"File does not exist: {full_path}", status=404)
