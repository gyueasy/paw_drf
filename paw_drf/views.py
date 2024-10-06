from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

def test_view(request):
    return HttpResponse("Test view is working")