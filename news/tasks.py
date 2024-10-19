from celery import shared_task
from django.conf import settings
from pytz import timezone
from datetime import datetime
import feedparser
import openai
import logging
import json
from .models import NewsItem, News

openai.api_key = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

@shared_task
def fetch_crypto_news():
    feeds = News.objects.filter(is_active=True)
    if not feeds.exists():
        default_feeds = [
            {'name': 'CoinDesk', 'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/'},
            {'name': 'Cointelegraph', 'url': 'https://cointelegraph.com/rss'}
        ]
    else:
        default_feeds = [{'name': feed.name, 'url': feed.url} for feed in feeds]

    kr_tz = timezone('Asia/Seoul')
    news_items = []

    for feed in default_feeds:
        try:
            parsed_feed = feedparser.parse(feed['url'])
        except Exception as e:
            print(f"Error parsing feed {feed['name']}: {str(e)}")
            continue

        if not parsed_feed.entries:  # entries가 비어있다면 넘어가기
            print(f"No entries found for feed {feed['name']}")
            continue

        for entry in parsed_feed.entries:
            title = entry.title[:500]  # 500자로 제한
            link = entry.link
            summary = entry.summary[:5000] if 'summary' in entry else "요약 정보 없음"  # 적절한 길이로 제한

            # Time parsing 부분에서 예외 처리 추가
            try:
                if feed['name'] == 'CoinDesk':
                    utc_time = datetime(*entry.published_parsed[:6])
                else:  # Cointelegraph
                    utc_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                kr_time = utc_time.astimezone(kr_tz)
                published = kr_time
            except Exception as e:
                print(f"Error processing time for entry {title}: {str(e)}")
                continue  # 시간을 처리할 수 없으면 다음으로 넘어가기

            image_url = extract_image_url(entry, feed['name'])

            news_feed, _ = News.objects.get_or_create(name=feed['name'], defaults={'url': feed['url'], 'is_active': True})

            news_item, created = NewsItem.objects.update_or_create(
                link=link,
                defaults={
                    'feed': news_feed,
                    'title': title,
                    'content': summary,
                    'published_date': published,
                    'image_url': image_url
                }
            )

            if created:  # 새로 생성된 경우에만
                news_items.append(news_item)

                # 필드 길이 로그 출력
                logger.info(f"Title length: {len(news_item.title)}")
                logger.info(f"Content length: {len(news_item.content)}")
                logger.info(f"Published date: {news_item.published_date}")
                logger.info(f"Link length: {len(news_item.link)}")
                logger.info(f"Image URL length: {len(news_item.image_url) if news_item.image_url else 0}")

                # OpenAI 분석 수행
                try:
                    analysis_result = analyze_with_openai(news_item)
                    if analysis_result:
                        news_item.ai_analysis = analysis_result
                        news_item.translated_title = analysis_result.get('translated_title', '')
                        news_item.translated_content = analysis_result.get('translated_content', '')
                        news_item.impact = analysis_result.get('impact', '')
                        news_item.tickers = ','.join(analysis_result.get('tickers', []))
                        news_item.save()
                except Exception as e:
                    print(f"Error analyzing news item {title}: {str(e)}")

    return f"{len(news_items)} new items fetched, saved, and analyzed."



def extract_image_url(entry, source):
    if source == 'CoinDesk':
        if 'media_content' in entry:
            media_contents = entry.media_content
            if media_contents:
                return media_contents[0]['url']
    elif source == 'Cointelegraph':
        if 'media_content' in entry:
            return entry.media_content[0]['url']
    return "이미지 URL 없음"

def analyze_with_openai(news_item):
    prompt = f"""
    제목: {news_item.title}
    내용: {news_item.content}

    위의 암호화폐 관련 뉴스를 분석하여 다음 정보를 JSON 형식으로 제공해주세요:
    1. 번역된 제목과 내용
    2. 뉴스의 전반적인 감정 (Bull, Bear, Neutral 중 하나)
    3. 뉴스에서 언급된 암호화폐 티커 심볼 (없으면 빈 리스트)
    4. 이 뉴스가 암호화폐 시장에 미칠 수 있는 영향 (낮음, 중간, 높음 중 하나)
    5. AI 분석 결과 (짧은 코멘트)
    예시:
    {{
        "translated_title": "번역된 제목",
        "translated_content": "번역된 내용",
        "market_sentiment": "Bull",
        "tickers": ["BTC", "ETH"],
        "impact": "높음",
        "ai_analysis": "짧은코멘트"
    }}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.0-mini",
            messages=[
                {"role": "system", "content": "너는 뉴스 분석 전문가야. 그리고 암호화폐에 대해 잘 알고 있어. 또한 번역도 가능해."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        analysis = json.loads(response.choices[0].message['content'])
        return analysis
    except Exception as e:
        print(f"Error in OpenAI analysis: {str(e)}")
        return None
