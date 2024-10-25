from flask import Flask, render_template, jsonify, request
import requests
from config import GDATA_API_KEY  # config 파일에서 API 키 가져오기

app = Flask(__name__)


# 공공데이터 포탈 API 키
API_KEY = GDATA_API_KEY  # config.py에서 API 키 가져오기


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_farm_data', methods=['GET'])
def get_farm_data():
    farm_code = request.args.get('farm_code')

    url = "https://apis.data.go.kr/1390000/SmartFarmdata/envdatarqst"  # 엔드포인트 확인
    params = {
        "serviceKey": API_KEY,
        "pageSize": 100,
        "searchFrmhsCode": farm_code,
        "returnType": "json"
    }

    response = requests.get(url, params=params)

    # 에러처리 추가
    if response.status_code == 200:
        try:
            data = response.json()
            return jsonify(data)
        except ValueError:
            return jsonify({"error": "Invalid JSON response", "response": response.text})
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code


if __name__ == "__main__":
    app.run(debug=True)
