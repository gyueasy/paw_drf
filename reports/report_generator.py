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


def generate_reports():
    try:
        # 1. 차트 분석
        logger.info("Starting chart analysis")
        chart_result = capture_and_analyze_chart()
        logger.info("Chart analysis completed")

        # 2. 뉴스 크롤링 및 분석
        logger.info("Starting news crawling and analysis")
        news_result = crawl_and_analyze_news()
        logger.info("News analysis completed")

        # 3. Accuracy 계산
        logger.info("Calculating accuracy")
        accuracy = calculate_accuracy()
        logger.info(f"Accuracy calculated: {accuracy}")

        # 4. 회고 분석
        logger.info("Starting retrospective analysis")
        retrospective_result = create_and_analyze_retrospective_report()
        logger.info("Retrospective analysis completed")

        # 5. 메인 리포트 생성
        logger.info("Generating main report")
        main_report = create_main_report()
        logger.info("Main report generated")

        logger.info("All reports generated successfully")
    except Exception as e:
        logger.error(
            f"Error occurred during report generation: {str(e)}", exc_info=True)
