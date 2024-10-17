from celery import shared_task, chain, chord
from reports.services import ChartService
from reports.services import NewsService
from reports.services import OpenAIService
from reports.models import NewsReport
from reports.services import ReportService, RetrospectiveReportService
from reports.models import Accuracy, MainReport, Price
import logging
import json

logger = logging.getLogger(__name__)

@shared_task
def capture_and_analyze_chart_task():
    chart_service = ChartService()
    result = chart_service.capture_and_analyze_chart()
    return result.get('chart_report_id') if result.get('success') else None

@shared_task
def crawl_and_analyze_news_task():
    try:
        news_service = NewsService()
        news_items = news_service.crawl_news()
        
        openai_service = OpenAIService()
        analysis_result = openai_service.analyze_news(news_items)
        
        if "error" in analysis_result:
            logger.error(f"Analysis error: {analysis_result['error']}")
            return None
        
        news_report = NewsReport(
            news_analysis=json.dumps(analysis_result)
        )
        news_report.save()
        
        return {
            'success': True,
            'message': '뉴스가 성공적으로 크롤링, 분석 및 저장되었습니다.',
            'news_report_id': news_report.id,
            'created_at': news_report.created_at.isoformat(),
            'analysis_summary': {
                'market_sentiment': analysis_result.get('market_sentiment', ''),
                'key_events_count': len(analysis_result.get('key_events', [])),
                'potential_impact': analysis_result.get('potential_impact', ''),
                'notable_trends_count': len(analysis_result.get('notable_trends', []))
            }
        }
    except Exception as e:
        logger.error(f"뉴스 크롤링 및 분석 중 오류 발생: {str(e)}")
        return None

@shared_task
def calculate_accuracy_task():
    try:
        new_accuracy = Accuracy.calculate_and_save_accuracy()
        return {
            'accuracy': new_accuracy.accuracy,
            'average_accuracy': f"{new_accuracy.average_accuracy:.2f}%",
            'recommendation': new_accuracy.recommendation,
            'recommendation_value': new_accuracy.recommendation_value,
            'price_change': f"{new_accuracy.price_change:.2f}%",
            'is_correct': new_accuracy.is_correct,
            'calculated_at': new_accuracy.calculated_at.isoformat(),
            'db_stats': {
                'main_reports_count': MainReport.objects.count(),
                'prices_count': Price.objects.count(),
                'accuracies_count': Accuracy.objects.count()
            }
        }
    except Exception as e:
        logger.error(f"Error in calculate_accuracy_task: {str(e)}")
        raise

@shared_task
def create_and_analyze_retrospective_report_task():
    try:
        new_weights, message = RetrospectiveReportService.create_and_update_retrospective_report()
        if new_weights:
            return {
                'success': True,
                'message': message,
                'new_weights': new_weights.to_dict()
            }
        else:
            logger.error(message)
            return {
                'success': False,
                'error': message
            }
    except Exception as e:
        logger.error(f"회고 분석 및 가중치 업데이트 중 오류 발생: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def create_main_report_task():
    report_service = ReportService()
    try:
        main_report = report_service.create_main_report()
        if main_report:
            return {
                'success': True,
                'message': '메인 리포트가 성공적으로 생성되었습니다.',
                'report_id': main_report.id
            }
        else:
            return {
                'success': False,
                'message': '메인 리포트 생성에 실패했습니다.'
            }
    except Exception as e:
        logger.error(f"Error in create_main_report_task: {str(e)}")
        return {
            'success': False,
            'message': f'메인 리포트 생성 중 오류가 발생했습니다: {str(e)}'
        }

@shared_task
def generate_reports_task():
    try:
        logger.info("Starting generate_reports_task")

        # 차트 분석과 뉴스 크롤링을 병렬로 실행
        chart_task = capture_and_analyze_chart_task.s()
        news_task = crawl_and_analyze_news_task.s()
        
        chord_task = chord((chart_task, news_task), _process_chart_and_news_results.s())
        
        # 나머지 태스크들을 체인으로 연결
        result = chain(
            chord_task,
            calculate_accuracy_task.s(),
            create_and_analyze_retrospective_report_task.s(),
            create_main_report_task.s()
        )()

        logger.info("Finished generate_reports_task")
        return {
            'success': True,
            'message': 'Report generation tasks have been initiated.'
        }
    except Exception as e:
        logger.error(f"Error in generate_reports_task: {str(e)}")
        return {
            'success': False,
            'error': f'리포트 생성 중 오류 발생: {str(e)}'
        }

@shared_task
def _process_chart_and_news_results(results):
    chart_result, news_result = results
    if not chart_result or not news_result:
        raise Exception("Chart analysis or news crawling failed")
    logger.info("Chart analysis and news crawling completed successfully")
    return results