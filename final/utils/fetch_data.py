import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

# API Key 설정
GDATA_API_KEY = "TEo5fURVg6O3ChvfXOmzkr0IXbTl0d4VkfIj3JVTz0ctJ+NS0IjPHxLXlijxDlubeXvzd3ZlGksTn/HhACp8gA=="


# ThingSpeak에서 데이터 가져오기 함수
def fetch_thingspeak_data(start_time, end_time):
    # 시작과 종료 시간을 ISO 8601 형식으로 변환
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    # API 요청 URL 생성
    url = f"https://api.thingspeak.com/channels/2328695/feeds.csv?start={start_str}&end={end_str}&api_key={GDATA_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        # 데이터를 읽고 컬럼 이름을 정리
        data = pd.read_csv(StringIO(response.text))
        data.columns = data.columns.str.lower().str.strip()  # 소문자 변환 및 공백 제거
        data = data.rename(columns={
            "field1": "temp",  # 온도
            "field2": "humid",  # 습도
            "field3": "radn",  # 일사량
            "field4": "wind",  # 풍속
            "field5": "rainfall",  # 강우량
            "field6": "battery"  # 배터리 전압
        })

        # created_at 컬럼을 날짜 형식으로 변환하고 시간대 설정
        data['created_at'] = pd.to_datetime(data['created_at'])
        if data['created_at'].dt.tz is None:
            data['created_at'] = data['created_at'].dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')
        else:
            data['created_at'] = data['created_at'].dt.tz_convert('Asia/Seoul')

        # created_at을 인덱스로 설정
        data = data.set_index('created_at')
        return data
    else:
        # 오류 메시지 출력
        print(f"데이터 로드 실패: {response.status_code}")
        return pd.DataFrame()


# 예시 사용
if __name__ == "__main__":
    # 여기서 start_time과 end_time을 자유롭게 설정할 수 있습니다.
    start_date = datetime.now() - timedelta(days=7)  # 예시: 일주일 전부터 오늘까지 데이터
    end_date = datetime.now()
    data = fetch_thingspeak_data(start_date, end_date)
    if not data.empty:
        print("데이터가 성공적으로 로드되었습니다:")
        print(data.head())
    else:
        print("데이터 로드 실패 또는 데이터가 없습니다.")
