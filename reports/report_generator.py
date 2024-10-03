from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from .views import (
    crawl_and_analyze_news, 
    capture_and_analyze_chart, 
    create_main_report, 
    create_and_analyze_retrospective_report, 
    calculate_accuracy
)
from .models import Accuracy
import logging

logger = logging.getLogger(__name__)

# 가짜 request 객체를 생성하는 함수
def create_fake_request():
    factory = RequestFactory()
    request = factory.post('/')
    request.user = AnonymousUser()
    return request

# 래퍼 함수들
def wrapper_capture_and_analyze_chart():
    request = create_fake_request()
    return capture_and_analyze_chart(request)

def wrapper_crawl_and_analyze_news():
    request = create_fake_request()
    return crawl_and_analyze_news(request)

def wrapper_create_main_report():
    request = create_fake_request()
    return create_main_report(request)

def wrapper_create_and_analyze_retrospective_report():
    request = create_fake_request()
    return create_and_analyze_retrospective_report(request)

def wrapper_calculate_accuracy():
    request = create_fake_request()
    return calculate_accuracy(request)

def generate_reports():
    try:
        # 1. 차트 분석
        logger.info("Starting chart analysis")
        chart_result = wrapper_capture_and_analyze_chart()
        logger.info("Chart analysis completed")

        # 2. 뉴스 크롤링 및 분석
        logger.info("Starting news crawling and analysis")
        news_result = wrapper_crawl_and_analyze_news()
        logger.info("News analysis completed")

        # 3. Accuracy 계산
        logger.info("Calculating accuracy")
        accuracy = wrapper_calculate_accuracy()
        logger.info(f"Accuracy calculated: {accuracy}")

        # 4. 회고 분석
        logger.info("Starting retrospective analysis")
        retrospective_result = wrapper_create_and_analyze_retrospective_report()
        logger.info("Retrospective analysis completed")

        # 5. 메인 리포트 생성
        logger.info("Generating main report")
        main_report = wrapper_create_main_report()
        logger.info("Main report generated")

        logger.info("All reports generated successfully")
    except Exception as e:
        logger.error(
            f"Error occurred during report generation: {str(e)}", exc_info=True)