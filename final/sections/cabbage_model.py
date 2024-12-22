import requests
import base64
import time
import streamlit as st


def show():
    # Streamlit 페이지 구성
    st.title("🌱 스마트팜 모델 실행 대시보드")
    st.sidebar.header("API 설정")

    # API 키 입력
    apikey = st.sidebar.text_input("API Key", type="password")

    # 기본 API URL 설정
    urlm = 'https://pycabbage-api.camp.re.kr/Pycabbage'

    # 파일을 Base64로 인코딩
    def fileToBase64(filepath):
        with open(filepath, "rb") as file:
            data = file.read()
        return base64.b64encode(data).decode("utf-8")



    # API 함수들
    # def download_sample_file():
    #     url = f"{urlm}/getSample"
    #     param = {"apiKey": apikey}
    #     res = requests.post(url=url, json=param)
    #
    #     if res.status_code == 200:
    #         file_path = 'Sample.zip'
    #         with open(file_path, 'wb') as file:
    #             file.write(res.content)
    #         st.success("샘플 파일 다운로드 성공")
    #         return file_path
    #     else:
    #         st.error(f"샘플 파일 다운로드 실패: {res.status_code}")
    #         st.stop()

        # 파일을 Base64로 인코딩

    def create_session():
        url = f"{urlm}/connect"
        param = {"apiKey": apikey}
        res = requests.post(url=url, json=param)
        if res.status_code == 200:
            jobid = res.content.decode('utf-8')
            st.success(f"세션 생성 성공: {jobid}")
            return jobid
        else:
            st.error(f"세션 생성 실패: {res.status_code}")
            st.stop()

    def launch_model(jobid, inputfile):
        url = f"{urlm}/launch"
        params = {"apiKey": apikey, "jobid": jobid, "file": inputfile}
        res = requests.post(url=url, json=params)
        if res.status_code == 200:
            st.success("모델 실행 성공")
        else:
            st.error(f"모델 실행 실패: {res.status_code}")
            st.stop()

    def check_status(jobid, timeout=300):
        url = f"{urlm}/getStatus"
        params = {"apiKey": apikey, "jobid": jobid}

        start_time = time.time()
        with st.spinner("모델 실행 중... 잠시만 기다려 주세요."):
            while True:
                res = requests.post(url, json=params)
                if res.status_code == 200:
                    status = res.content.decode('utf-8')
                    if status == "completed":
                        st.success("모델 실행 완료")
                        return
                    elif status == "failed":
                        st.error("모델 실행 실패")
                        st.stop()
                    else:
                        st.info("모델 실행 중...")
                else:
                    st.error(f"상태 확인 실패: {res.status_code}")
                    st.stop()

                # 타임아웃 체크
                if time.time() - start_time > timeout:
                    st.error("모델 실행이 타임아웃되었습니다.")
                    st.stop()

                time.sleep(3)

    def download_output(jobid):
        url = f"{urlm}/getOutput"
        params = {"apiKey": apikey, "jobid": jobid, "variable": "all"}
        res = requests.post(url, json=params)

        if res.status_code == 200:
            file_path = 'output.zip'
            with open(file_path, 'wb') as file:
                file.write(res.content)
            st.success(f"출력 파일 저장 성공: {file_path}")
            with open(file_path, "rb") as file:
                st.download_button(
                    label="📥 출력 파일 다운로드",
                    data=file,
                    file_name="output.zip",
                    mime="application/zip"
                )
        else:
            st.error(f"출력 파일 저장 실패: {res.status_code}")
            st.stop()

    def disconnect_session(jobid):
        url = f"{urlm}/disconnect"
        params = {"apiKey": apikey, "jobid": jobid}
        res = requests.post(url, json=params)
        if res.status_code == 200:
            st.success("세션 종료 성공")
        else:
            st.error(f"세션 종료 실패: {res.status_code}")
            st.stop()

    # 실행 버튼
    if st.sidebar.button("모델 실행 시작"):
        if not apikey:
            st.error("API 키를 입력하세요.")
            st.stop()

        try:
            # 작업 흐름 실행
            # sample_file = download_sample_file()
            # 파일 경로 사용
            sample_file_path = "/Users/sola/Documents/GitHub/2024_SAP/final/file/Sample.zip"
            inputfile = fileToBase64(sample_file_path)
            jobid = create_session()
            launch_model(jobid, inputfile)
            check_status(jobid)
            download_output(jobid)
            disconnect_session(jobid)

        except Exception as e:
            st.error(f"오류 발생: {e}")