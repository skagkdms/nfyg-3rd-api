# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
# re 모듈은 이번 기능에서는 필요 없어서 제거했습니다.

app = Flask(__name__)

CORS(app)

# -------------------------------------------------------------
# 기존 기능: 랜덤 숫자 생성 API
# -------------------------------------------------------------
@app.route('/api/random')
def random_number():
    """1부터 99 사이의 랜덤한 정수를 생성하고 JSON 형태로 반환합니다."""
    number = random.randint(1, 99)
    return jsonify({'number': number})

# -------------------------------------------------------------
# 새로 추가된 기능: 문장 부호 및 길이 일관성 검증 API
# -------------------------------------------------------------
@app.route('/api/validate-consistency', methods=['POST'])
def validate_consistency():
    """
    원문과 번역문을 입력받아 문장 부호가 일치하는지,
    길이가 너무 크게 차이나지 않는지 검증합니다.
    """
    data = request.get_json()

    if not data or 'source_text' not in data or 'translated_text' not in data:
        return jsonify({"error": "Missing 'source_text' or 'translated_text'"}), 400

    source = data['source_text'].strip()
    translated = data['translated_text'].strip()
    
    warnings = []

    # 1. 문장 부호 검증 (마지막 글자 확인)
    # 확인하고 싶은 주요 문장 부호들
    punctuations = ['?', '!', '.']
    
    for p in punctuations:
        # 원문은 이 부호로 끝나는데, 번역문은 그렇지 않은 경우
        if source.endswith(p) and not translated.endswith(p):
            # 단, 스페인어의 물음표/느낌표(¿ ¡) 같은 예외는 이 간단한 로직으로는 처리하지 못합니다.
            warnings.append(f"문장 부호 불일치: 원문은 '{p}'로 끝나지만 번역문은 그렇지 않습니다.")

    # 2. 길이 비율 검증
    len_source = len(source)
    len_translated = len(translated)
    
    # 원문의 길이가 0이면 비율 계산이 불가능하므로 예외 처리
    if len_source > 0:
        ratio = len_translated / len_source
        
        # 번역문이 원문보다 3배 이상 길면 경고 (UI 깨짐 위험)
        if ratio > 3.0:
             warnings.append(f"길이 경고: 번역문이 원문보다 너무 깁니다. (약 {ratio:.1f}배)")
        # 번역문이 원문의 20% 미만이면 경고 (내용 누락 위험)
        elif ratio < 0.2:
             warnings.append(f"길이 경고: 번역문이 원문보다 너무 짧습니다. (약 {ratio:.1f}배)")
    else:
        ratio = 0

    # 경고가 하나도 없으면 True, 하나라도 있으면 False
    is_consistent = (len(warnings) == 0)

    return jsonify({
        'is_consistent': is_consistent,
        'warnings': warnings,
        'details': {
            'source_length': len_source,
            'translated_length': len_translated,
            'ratio': round(ratio, 2) 
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
