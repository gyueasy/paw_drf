from celery import shared_task
from .models import Discussion, AIComment
import openai
import json
import os

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

@shared_task
def generate_ai_comments(discussion_id):
    discussion = Discussion.objects.get(id=discussion_id)

    traders = [
        {"name": "Warren Buffett", "description": "가치 투자 전략"},
        {"name": "George Soros", "description": "글로벌 거시경제 전략"},
        {"name": "Ray Dalio", "description": "리스크 패리티 전략"},
        {"name": "Peter Lynch", "description": "성장주 투자 전략"},
        {"name": "Paul Tudor Jones", "description": "기술적 분석 및 단기 트레이딩"},
        {"name": "워뇨띠", "description": "100억 부자 스캘핑 트레이더, 횡보하거나 알트변동이 커지면 비중을 줄임, 캔들 여러개랑 거래량 묶어서 전체적인 패턴을 보는 트레이더"},
        {"name": "박호두", "description": "유튜브 트레이더, 해외선물과 암호화폐 트레이딩을 주로 다루는 트레이더, 굉장히 공격적인 투자 전략을 가지고 있음, "}
    ]

    prompt = f"""다음 토론 주제에 대해 트레이더들이 서로 토론하는 내용을 생성해주세요. 각 트레이더의 특성과 전략을 고려하여 자연스러운 대화를 만들어주세요.
박호두 말투:
- 어쩔 수 없는 소녀인가봐: 박호두가 포지션을 잡은 후 겁이 난 나머지 소액을 익절해버릴 때 하는 유행어. 변형으로는 "어쩔 수 없는 보이스카웃인가봐", "어쩔 수 없는 파트라슈인가봐", "어쩔 수 없는 닌텐도인가봐", "어쩔 수 없는 다이슨인가봐" 등이 있다.
- 지금이니?!!?: 포지션을 들어가거나 청산할 때 고민하면서 내뱉는 멘트.
- 푸근하네~: 상황이 생각한대로 흘러가 기분이 좋거나 가지고 있는 포지션의 방향으로 원웨이가 나올 때 하는 말이다. 


토론 주제: {discussion.title}
토론 내용: {discussion.content}

트레이더 정보:
{', '.join([f"{t['name']}({t['description']})" for t in traders])}

토론 형식:
[
  {{
    "trader": "트레이더 이름",
    "strategy": "트레이더 전략",
    "comment": "트레이더의 코멘트"
  }},
  ...
]

최소 7개의 코멘트를 생성해주세요. 트레이더들이 서로의 의견에 반응하고 토론하는 내용을 포함해주세요."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.0-mini",
            messages=[
                {"role": "system", "content": "당신은 다양한 투자 전략을 가진 트레이더들의 토론을 생성하는 AI 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        # OpenAI의 응답에서 생성된 토론 내용 추출
        generated_discussion = json.loads(response.choices[0].message.content)

        # JSON 결과 생성
        json_response = json.dumps({"discussion": generated_discussion}, ensure_ascii=False)

        # 코멘트를 데이터베이스에 저장
        for comment in generated_discussion:
            AIComment.objects.create(
                discussion=discussion,
                role=comment["trader"],
                strategy=comment["strategy"],
                content=comment["comment"]
            )

        return json_response

    except Exception as e:
        print(f"Error generating discussion: {str(e)}")
        return json.dumps({"error": "Failed to generate discussion"})