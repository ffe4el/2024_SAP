import os
import pandas as pd
import json
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from io import StringIO
import requests

# Google Drive 인증 설정
def authenticate_gdrive():
    gauth = GoogleAuth()
    # 환경 변수에서 Google Drive 인증 정보 로드
    creds_dict = json.loads(os.environ["GDRIVE_CREDENTIALS"])
    gauth.credentials = gauth.service_account_credentials_from_dict(creds_dict)
    drive = GoogleDrive(gauth)
    return drive

# 데이터 API로부터 데이터 가져오기
def fetch_weather_data(year, month, day):
    api_url = f"http://203.239.47.148:8080/dspnet.aspx?Site=85&Dev=1&Year={year}&Mon={month}&Day={day}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text
    else:
        raise ValueError("API에서 데이터를 가져오는데 실패했습니다.")

# 데이터를 DataFrame으로 변환하는 함수
def process_weather_data(data_text):
    data_io = StringIO(data_text)
    df = pd.read_csv(data_io, header=None)
    df.columns = ['timestamp', 'temp', 'humid', 'X1', 'X2', 'X3', 'X4', 'radn', 'wind_direction', 'X5', 'X6', 'X7',
                  'X8', 'X9', 'wind', 'rainfall', 'max_wind', 'battery']
    df = df[['timestamp', 'temp', 'humid', 'radn', 'wind', 'rainfall', 'battery']]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Google Drive에 CSV 파일 업로드 함수
def upload_to_gdrive(file_path, drive, folder_id=None):
    file = drive.CreateFile({"title": os.path.basename(file_path), "parents": [{"id": folder_id}] if folder_id else []})
    file.SetContentFile(file_path)
    file.Upload()

# 메인 함수
def main():
    # Google Drive 인증 및 객체 생성
    drive = authenticate_gdrive()

    # 현재 날짜 가져오기
    current_date = datetime.now()
    year, month, day = current_date.year, current_date.month, current_date.day

    # API로부터 데이터 가져오기 및 처리
    data_text = fetch_weather_data(year, str(month).zfill(2), str(day).zfill(2))
    weather_data = process_weather_data(data_text)

    # CSV 파일로 저장
    file_path = f'./weather_data/{year}_{month}.csv'
    os.makedirs('./weather_data', exist_ok=True)
    weather_data.to_csv(file_path, index=False)

    # Google Drive에 업로드
    upload_to_gdrive(file_path, drive, folder_id="1vSqClGRZev6VgkRf_2Kdpd_fJEvpPj5p")

if __name__ == '__main__':
    main()