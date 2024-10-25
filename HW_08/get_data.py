import os
import pandas as pd
from datetime import datetime
import requests

# 데이터 API에서 날씨 데이터 가져오기 함수
def get_aws(year, month, day):
    api_url = f"http://203.239.47.148:8080/dspnet.aspx?Site=85&Dev=1&Year={year}&Mon={month}&Day={day}"
    response = requests.get(api_url)
    data = response.text.strip().split('\n')
    df = pd.DataFrame([line.split(',') for line in data])

    timestamp = pd.to_datetime(df.iloc[:, 0])
    temp = pd.to_numeric(df.iloc[:, 1])
    humid = pd.to_numeric(df.iloc[:, 2])
    Radn = pd.to_numeric(df.iloc[:, 6])
    wind_from = pd.to_numeric(df.iloc[:, 7])
    wind = pd.to_numeric(df.iloc[:, 13])
    rain = pd.to_numeric(df.iloc[:, 14])
    battery = pd.to_numeric(df.iloc[:, 16])

    return pd.DataFrame({
        'timestamp': timestamp,
        'temp': temp,
        'humid': humid,
        'radn': Radn,
        'wind_from': wind_from,
        'wind': wind,
        'rain': rain,
        'battery': battery
    })


# CSV 파일에 새 데이터를 결합하고 중복 제거 후 저장
def save_to_csv(year, month, data):
    directory = './weather_data/'
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f'{year}_{month}.csv')

    if os.path.exists(file_path):
        # 기존 데이터 파일 읽기 (열 이름을 강제로 설정)
        existing_data = pd.read_csv(file_path, names=['timestamp', 'temp', 'humid', 'radn', 'wind_from', 'wind', 'rain',
                                                      'battery'], header=0)
        existing_data['timestamp'] = pd.to_datetime(existing_data['timestamp'])

        # 새 데이터와 결합 후 중복 제거 및 정렬
        merged_data = pd.concat([existing_data, data]).drop_duplicates('timestamp').sort_values('timestamp')
    else:
        merged_data = data

    merged_data.to_csv(file_path, index=False)


# 메인 함수
def main():
    current_date = datetime.now()
    year = current_date.year
    month = str(current_date.month).zfill(2)
    day = str(current_date.day).zfill(2)

    # 데이터 가져오기 및 CSV에 저장
    weather_data = get_aws(year, month, day)
    save_to_csv(year, month, weather_data)


if __name__ == '__main__':
    main()