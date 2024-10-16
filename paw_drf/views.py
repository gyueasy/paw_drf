from django.http import HttpResponse
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone

def health_check(request):
    return HttpResponse("OK")

def test_redis_cache(request):
    cache_key = 'test_key'
    cached_value = cache.get(cache_key)
    
    if cached_value is None:
        current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        cached_value = f"This is a test value set at {current_time}"
        cache.set(cache_key, cached_value, timeout=300)  # 5분 동안 캐시
        return JsonResponse({"cached_value": cached_value, "status": "newly set"})
    else:
        return JsonResponse({"cached_value": cached_value, "status": "from cache"})