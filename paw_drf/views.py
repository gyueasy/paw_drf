from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

def test_view(request, path):
    return HttpResponse(f"Requested media file: {path}")

