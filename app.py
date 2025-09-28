# app.py

# 필요한 모듈들을 가져옵니다.
from flask import Flask, jsonify, request # request는 POST 요청을 처리하기 위해 추가했습니다.
from flask_cors import CORS
import random
import re # 정규표현식을 사용하기 위해 re 모듈을 추가했습니다.

# Flask 애플리케이션을 생성합니다.
app = Flask(__name__)

# CORS(app)을 추가하여 모든 출처에서의 API 요청을 허용합니다.
# 이렇게 하면 Gemini Canvas와 같은 다른 도메인에서도 API를 호출할 수 있습니다.
CORS(app)

# -------------------------------------------------------------
# 기존 기능: 랜덤 숫자 생성 API
# -------------------------------------------------------------
# '/api/random' URL 경로에 대한 함수를 정의합니다.
# 이 경로로 GET 요청이 오면 이 함수가 실행됩니다.
@app.route('/api/random')
def random_number():
    """1부터 99 사이의 랜덤한 정수를 생성하고 JSON 형태로 반환합니다."""
    # 1부터 99 사이의 랜덤한 숫자를 생성합니다.
    number = random.randint(1, 99)
    # 생성된 숫자를 'number'라는 키와 함께 딕셔너리로 만듭니다.
    # jsonify는 딕셔너리를 JSON 응답으로 변환해줍니다.
    return jsonify({'number': number})

# -------------------------------------------------------------
# 새로 추가된 기능: 번역문 유효성 검증 API
# -------------------------------------------------------------
# '/api/validate-translation' URL 경로에 대한 함수를 정의합니다.
# 이 경로로 POST 요청이 오면 이 함수가 실행됩니다.
@app.route('/api/validate-translation', methods=['POST'])
def validate_translation():
    """
    원문(source_text)과 번역문(translated_text)을 JSON으로 입력받아,
    번역문의 플레이스홀더({})가 원문과 일치하는지 검증합니다.
    """
    # 1. 클라이언트가 보낸 JSON 데이터를 가져옵니다.
    data = request.get_json()

    # 2. 필요한 데이터('source_text', 'translated_text')가 있는지 확인합니다.
    if not data or 'source_text' not in data or 'translated_text' not in data:
        # 데이터가 없으면 400 에러를 반환합니다.
        return jsonify({"error": "Missing 'source_text' or 'translated_text' key in request body"}), 400

    source_text = data['source_text']
    translated_text = data['translated_text']
    
    # 3. 정규표현식을 사용해 원문과 번역문에서 각각 플레이스홀더를 찾습니다.
    # set()으로 감싸서 중복을 제거하고 비교하기 쉽게 만듭니다.
    source_placeholders = set(re.findall(r'\{.*?\}', source_text))
    translated_placeholders = set(re.findall(r'\{.*?\}', translated_text))

    # 4. 두 플레이스홀더 집합이 완전히 동일한지 비교합니다.
    is_valid = (source_placeholders == translated_placeholders)
    
    # 원문에는 있지만 번역문에는 없는 것 (누락된 플레이스홀더)
    missing = list(source_placeholders - translated_placeholders)
    
    # 번역문에는 있지만 원문에는 없는 것 (잘못 추가/변형된 플레이스홀더)
    added = list(translated_placeholders - source_placeholders)

    # 5. 검증 결과를 JSON으로 만들어 반환합니다.
    return jsonify({
        'is_valid': is_valid,
        'details': {
            'missing_in_translation': missing,
            'added_in_translation': added
        },
        'source_placeholders': sorted(list(source_placeholders)),
        'translated_placeholders': sorted(list(translated_placeholders))
    }), 200

# 이 스크립트가 직접 실행될 때 웹 서버를 구동합니다.
# render.com과 같은 서비스는 이 부분을 사용하여 앱을 실행합니다.
if __name__ == '__main__':
    # host='0.0.0.0'은 외부에서 접속 가능하도록 설정합니다.
    # Render.com은 PORT 환경변수를 통해 포트를 지정해 주므로, 그 값을 사용합니다.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
