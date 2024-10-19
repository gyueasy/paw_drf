from celery import shared_task, chain, chord
from reports.services import (
    ChartService,
    NewsService,
    OpenAIService,
    ReportService,
    RetrospectiveReportService,
)
from reports.models import NewsReport, Accuracy, MainReport, Price
import logging
import json

logger = logging.getLogger(__name__)


def _create_task_result(success: bool, message: str, **kwargs) -> dict:
    """
    Task 결과를 위한 dictionary를 생성합니다.

    Args:
        success (bool): Task 성공 여부
        message (str): 결과 메시지
        **kwargs: 추가적인 결과 데이터

    Returns:
        dict: 결과 dictionary
    """
    result = {
        "success": success,
        "message": message,
    }
    result.update(kwargs)
    return result


@shared_task
def capture_and_analyze_chart_task() -> dict:
    """
    차트를 캡처하고 분석하는 task입니다.

    Returns:
        dict: 성공 여부, 메시지, chart_report_id를 포함하는 dictionary
    """
    logger.info("Starting capture_and_analyze_chart_task")
    try:
        chart_service = ChartService()
        result = chart_service.capture_and_analyze_chart()
        if result.get("success"):
            logger.info(f"Chart analysis result: {result}")
            return _create_task_result(
                True,
                "차트 분석이 성공적으로 완료되었습니다.",
                chart_report_id=result.get("chart_report_id"),
            )
        else:
            logger.error(f"차트 분석에 실패했습니다: {result.get('error')}")
            return _create_task_result(False, "차트 분석에 실패했습니다.")
    except Exception as e:
        logger.error(f"Error in capture_and_analyze_chart_task: {str(e)}", exc_info=True)
        return _create_task_result(False, f"차트 분석 중 오류 발생: {str(e)}")


@shared_task
def crawl_and_analyze_news_task() -> dict:
    """
    뉴스를 크롤링하고 분석하는 task입니다.

    Returns:
        dict: 성공 여부, 메시지, news_report_id, created_at, analysis_summary를 포함하는 dictionary
    """
    logger.info("Starting crawl_and_analyze_news_task")
    try:
        news_service = NewsService()
        news_items = news_service.crawl_news()

        openai_service = OpenAIService()
        analysis_result = openai_service.analyze_news(news_items)

        news_report = NewsReport(news_analysis=json.dumps(analysis_result))
        news_report.save()

        logger.info(f"News analysis completed. Report ID: {news_report.id}")
        return _create_task_result(
            True,
            "뉴스가 성공적으로 크롤링, 분석 및 저장되었습니다.",
            news_report_id=news_report.id,
            created_at=news_report.created_at.isoformat(),
            analysis_summary={
                "market_sentiment": analysis_result.get("market_sentiment", ""),
                "key_events_count": len(analysis_result.get("key_events", [])),
                "potential_impact": analysis_result.get("potential_impact", ""),
                "notable_trends_count": len(analysis_result.get("notable_trends", [])),
            },
        )
    except Exception as e:
        logger.error(f"뉴스 크롤링 및 분석 중 오류 발생: {str(e)}", exc_info=True)
        return _create_task_result(False, f"뉴스 크롤링 및 분석 중 오류 발생: {str(e)}")


@shared_task
def calculate_accuracy_task(previous_results=None) -> dict:
    """
    정확도를 계산하는 task입니다.

    Returns:
        dict: accuracy, average_accuracy, recommendation, recommendation_value,
              price_change, is_correct, calculated_at, db_stats를 포함하는 dictionary
    """
    logger.info(f"Starting calculate_accuracy_task with previous_results: {previous_results}")
    try:
        new_accuracy = Accuracy.calculate_and_save_accuracy()
        result = {
            "accuracy": new_accuracy.accuracy,
            "average_accuracy": f"{new_accuracy.average_accuracy:.2f}%",
            "recommendation": new_accuracy.recommendation,
            "recommendation_value": new_accuracy.recommendation_value,
            "price_change": f"{new_accuracy.price_change:.2f}%",
            "is_correct": new_accuracy.is_correct,
            "calculated_at": new_accuracy.calculated_at.isoformat(),
            "db_stats": {
                "main_reports_count": MainReport.objects.count(),
                "prices_count": Price.objects.count(),
                "accuracies_count": Accuracy.objects.count(),
            },
        }
        logger.info(f"Accuracy calculation completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in calculate_accuracy_task: {str(e)}", exc_info=True)
        raise  # 예외를 다시 발생시켜 Celery에게 task 실패를 알립니다.


@shared_task
def create_and_analyze_retrospective_report_task(previous_results=None) -> dict:
    """
    회고 분석 보고서를 생성하고 분석하는 task입니다.

    Returns:
        dict: 성공 여부, 메시지, new_weights를 포함하는 dictionary
    """
    logger.info(f"Starting create_and_analyze_retrospective_report_task with previous_results: {previous_results}")
    try:
        new_weights, message = RetrospectiveReportService.create_and_update_retrospective_report()
        if new_weights:
            result = _create_task_result(
                True, message, new_weights=new_weights.to_dict()
            )
            logger.info(f"Retrospective report created: {result}")
            return result
        else:
            logger.error(message)
            return _create_task_result(False, message)
    except Exception as e:
        logger.error(
            f"회고 분석 및 가중치 업데이트 중 오류 발생: {str(e)}", exc_info=True
        )
        return _create_task_result(False, f"회고 분석 및 가중치 업데이트 중 오류 발생: {str(e)}")

@shared_task
def create_main_report_task(previous_results=None) -> dict:
    """
    메인 보고서를 생성하는 task입니다.

    Returns:
        dict: 성공 여부, 메시지, report_id를 포함하는 dictionary
    """
    logger.info(f"Starting create_main_report_task with previous_results: {previous_results}")
    report_service = ReportService()
    try:
        logger.info("Calling create_main_report method")
        main_report = report_service.create_main_report()
        if main_report:
            result = _create_task_result(
                True, "메인 리포트가 성공적으로 생성되었습니다.", report_id=main_report.id
            )
            logger.info(f"Main report created: {result}")
            return result
        else:
            logger.error("Main report creation failed: ReportService.create_main_report returned None")
            return _create_task_result(False, "메인 리포트 생성에 실패했습니다. ReportService.create_main_report가 None을 반환했습니다.")
    except Exception as e:
        logger.error(f"Error in create_main_report_task: {str(e)}", exc_info=True)
        return _create_task_result(
            False, f"메인 리포트 생성 중 오류가 발생했습니다: {str(e)}"
        )


from celery import shared_task
from django.core.cache import cache
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def generate_reports_task() -> dict:
    """
    모든 보고서 생성 task를 실행하는 task입니다.

    Returns:
        dict: 성공 여부, 메시지, task_id를 포함하는 dictionary
    """
    lock_id = "generate_reports_lock"
    acquire_lock = lambda: cache.add(lock_id, "true", 60*60)  # 1시간 락
    release_lock = lambda: cache.delete(lock_id)

    if acquire_lock():
        try:
            logger.info("Starting generate_reports_task")
            
            # 차트 분석과 뉴스 크롤링을 병렬로 실행
            chart_task = capture_and_analyze_chart_task.s()
            news_task = crawl_and_analyze_news_task.s()

            # 병렬 작업 후 순차적으로 실행할 태스크들을 체인으로 연결
            task_chain = chain(
                chord((chart_task, news_task), _process_chart_and_news_results.s()),
                calculate_accuracy_task.s(),
                create_and_analyze_retrospective_report_task.s(),
                create_main_report_task.s()
            )
            
            # 체인 실행
            result = task_chain.delay()
            
            logger.info("All tasks have been initiated in generate_reports_task")
            return {
                'success': True,
                'message': 'Report generation tasks have been initiated.',
                'task_id': result.id
            }
        except Exception as e:
            logger.error(f"Error in generate_reports_task: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'리포트 생성 중 오류 발생: {str(e)}'
            }
        finally:
            release_lock()
    else:
        logger.info("generate_reports_task is already running")
        return {
            'success': False,
            'message': 'Report generation is already in progress.'
        }

@shared_task
def _process_chart_and_news_results(results):
    logger.info(f"Received results: {results}")
    try:
        chart_result, news_result = results
        logger.info(f"Chart result: {chart_result}")
        logger.info(f"News result: {news_result}")
        if not chart_result or not news_result:
            raise Exception("Chart analysis or news crawling failed")
        logger.info("Chart analysis and news crawling completed successfully")
        return {
            'chart_result': chart_result,
            'news_result': news_result
        }
    except Exception as e:
        logger.error(f"Error in _process_chart_and_news_results: {str(e)}", exc_info=True)
        raise