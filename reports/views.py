from django.http import JsonResponse
from .services import ChartService, OpenAIService
from django.conf import settings
import time
import os
import json
from django.views.decorators.csrf import csrf_exempt
from .models import ChartReport

@csrf_exempt
def capture_and_analyze_chart(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
    chart_service = ChartService()
    openai_service = OpenAIService()
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"chart_screenshot_{timestamp}.png"
    
    screenshot_path = chart_service.take_screenshot(
        "https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC",
        filename
    )
    
    image_url = request.build_absolute_uri(settings.MEDIA_URL + 'capture_chart/' + filename)
    
    analysis_result = openai_service.analyze_chart(screenshot_path)
    
    if "error" in analysis_result:
        return JsonResponse({
            "status": "error",
            "image_url": image_url,
            "timestamp": timestamp,
            "error_message": analysis_result["error"]
        }, status=500)
    
    try:
        chart_report = ChartReport(
            image_url=image_url,
            technical_analysis=analysis_result["Technical Analysis"],
            candlestick_analysis=analysis_result["Candlestick Patterns"],
            moving_average_analysis=analysis_result["Moving Averages"],
            bollinger_bands_analysis=analysis_result["Bollinger Bands"],
            rsi_analysis=analysis_result["RSI"],
            fibonacci_retracement_analysis=analysis_result["Fibonacci Retracement"],
            macd_analysis=analysis_result["MACD"],
            support_resistance_analysis=analysis_result["Support and Resistance Levels"],
            overall_recommendation=analysis_result["Overall Recommendation"]
        )
        chart_report.save()
        print("Chart report saved successfully!")
    except Exception as e:
        print(f"Error saving chart report: {str(e)}")
        return JsonResponse({
            "status": "error",
            "image_url": image_url,
            "timestamp": timestamp,
            "error_message": f"Error saving chart report: {str(e)}"
        }, status=500)

    return JsonResponse({
        "status": "success",
        "image_url": image_url,
        "timestamp": timestamp,
        "analysis": analysis_result
    })