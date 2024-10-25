import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API 설정
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = "1vSqClGRZev6VgkRf_2Kdpd_fJEvpPj5p"

def authenticate_gdrive():
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def upload_to_gdrive(service, folder_id, file_path):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_path} with file ID: {file.get('id')}")

def main():
    service = authenticate_gdrive()
    weather_data_dir = "./weather_data"

    if os.path.exists(weather_data_dir):
        for filename in os.listdir(weather_data_dir):
            file_path = os.path.join(weather_data_dir, filename)
            if os.path.isfile(file_path):
                upload_to_gdrive(service, FOLDER_ID, file_path)

if __name__ == "__main__":
    main()