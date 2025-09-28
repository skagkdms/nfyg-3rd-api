# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import re # 정규표현식(Regex)을 사용하기 위해 re 모듈을 import 합니다.

app = Flask(__name__)

CORS(app) # 모든 경로에 대해 CORS를 허용합니다.

# --- 기존 API 엔드포인트 ---
@app.route('/api/random')
def random_number():
    """1부터 99 사이의 랜덤한 정수를 생성하고 JSON 형태로 반환합니다."""
    number = random.randint(1, 99)
    return jsonify({'number': number})

# --- 새로 추가된 API 엔드포인트 ---
@app.route('/api/validate-translation', methods=['POST'])
def validate_translation():
    """
    원문(source)과 번역문(translated) 텍스트를 입력받아,
    번역문이 원문의 플레이스홀더({})를 잘 보존하고 있는지 검증합니다.

    예시 요청:
    POST /api/validate-translation
    {
        "source_text": "Welcome, {username}! You have {count} new messages.",
        "translated_text": "¡Bienvenido, {username}! Tienes {count} mensajes."
    }

    예시 성공 응답:
    {
        "is_valid": true,
        "details": {
            "missing_in_translation": [],
            "added_in_translation": []
        },
        "source_placeholders": ["{username}", "{count}"],
        "translated_placeholders": ["{username}", "{count}"]
    }
    
    예시 실패 응답 (플레이스홀더 누락):
    {
        "is_valid": false,
        "details": {
            "missing_in_translation": ["{count}"],
            "added_in_translation": []
        },
        "source_placeholders": ["{username}", "{count}"],
        "translated_placeholders": ["{username}"]
    }
    """
    # 1. 요청 본문에서 JSON 데이터를 가져옵니다.
    data = request.get_json()

    # 2. 필수 키('source_text', 'translated_text')가 있는지 확인합니다.
    if not data or 'source_text' not in data or 'translated_text' not in data:
        return jsonify({"error": "Missing 'source_text' or 'translated_text' key in request body"}), 400

    source_text = data['source_text']
    translated_text = data['translated_text']
    
    # 3. 정규표현식을 사용해 원문과 번역문에서 각각 플레이스홀더를 추출합니다.
    # set으로 만들어 중복을 제거하고 비교를 쉽게 합니다.
    source_placeholders = set(re.findall(r'\{.*?\}', source_text))
    translated_placeholders = set(re.findall(r'\{.*?\}', translated_text))

    # 4. 두 플레이스홀더 집합을 비교하여 유효성을 검증합니다.
    is_valid = (source_placeholders == translated_placeholders)
    
    # 원문에는 있지만 번역문에는 없는 플레이스홀더 (누락된 것)
    missing = list(source_placeholders - translated_placeholders)
    
    # 번역문에는 있지만 원문에는 없는 플레이스홀더 (추가/변형된 것)
    added = list(translated_placeholders - source_placeholders)

    # 5. 검증 결과를 JSON 형태로 만들어 반환합니다.
    return jsonify({
        'is_valid': is_valid,
        'details': {
            'missing_in_translation': missing,
            'added_in_translation': added
        },
        'source_placeholders': sorted(list(source_placeholders)),
        'translated_placeholders': sorted(list(translated_placeholders))
    }), 200

if __name__ == '__main__':
    # Render.com 환경에서는 'PORT' 환경 변수를 사용합니다.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
