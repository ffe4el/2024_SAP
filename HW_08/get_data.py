import requests
import pandas as pd
from datetime import datetime
from io import StringIO
import os


# API로부터 데이터 가져오기
def fetch_weather_data(year, month, day):
    api_url = f"http://203.239.47.148:8080/dspnet.aspx?Site=85&Dev=1&Year={year}&Mon={month}&Day={day}"
    response = requests.get(api_url)
    if response.status_code == 200:
        # 응답 데이터를 텍스트로 변환
        return response.text
    else:
        raise ValueError("API에서 데이터를 가져오는데 실패했습니다.")


# 데이터를 DataFrame으로 변환하는 함수
def process_weather_data(data_text):
    # 데이터를 DataFrame으로 변환
    data_io = StringIO(data_text)
    df = pd.read_csv(data_io, header=None)

    # 열 이름 설정
    df.columns = ['timestamp', 'temp', 'humid', 'X1', 'X2', 'X3', 'X4', 'radn', 'wind_direction', 'X5', 'X6', 'X7',
                  'X8', 'X9', 'wind', 'rainfall', 'max_wind', 'battery']

    # 필요 없는 열 제거
    df = df[['timestamp', 'temp', 'humid', 'radn', 'wind', 'rainfall', 'battery']]

    # 시간 형식 변환
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    return df


# 데이터를 CSV 파일로 저장하는 함수
def save_to_csv(year, month, day, data):
    directory = './weather_data/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, f'{year}_{month}.csv')

    if os.path.exists(file_path):
        # 기존 파일 읽고 중복 제거 후 저장
        existing_data = pd.read_csv(file_path)
        merged_data = pd.concat([existing_data, data], ignore_index=True).drop_duplicates('timestamp')
        merged_data.to_csv(file_path, index=False)
    else:
        # 새로운 파일 생성
        data.to_csv(file_path, index=False)

    if data.empty:
        print("데이터가 비어있습니다.")


# 메인 함수
def main():
    # 현재 날짜 가져오기
    current_date = datetime.now()
    year = current_date.year
    month = str(current_date.month).zfill(2)
    day = str(current_date.day).zfill(2)

    # API로부터 데이터 가져오기 및 처리
    data_text = fetch_weather_data(year, month, day)
    weather_data = process_weather_data(data_text)

    # 데이터를 CSV 파일로 저장
    save_to_csv(year, month, day, weather_data)


# 스크립트 실행
if __name__ == '__main__':
    main()