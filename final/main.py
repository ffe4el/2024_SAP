import streamlit as st
from datetime import datetime, timedelta
from sections import dashboard_explanation, csv_management, data_visualization, data_download, farm_chatbot, growth_model, rasp_camera
from utils.fetch_data import fetch_thingspeak_data
from matplotlib import rc
import os
import requests
import platform


# 데이터 업데이트 함수
def update_data():
    # 최근 일주일치 데이터를 가져오는 예시
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    data = fetch_thingspeak_data(start_date, end_date)
    st.session_state["data"] = data  # 데이터를 세션 상태에 저장

    # 로그 기록을 위해 세션 상태에 로그 초기화 및 추가
    if "log" not in st.session_state:
        st.session_state["log"] = []
    st.session_state["log"].append(f"{datetime.now()} - 데이터 업데이트 완료")

# 1분마다 자동으로 데이터 업데이트 설정
def auto_update():
    if "data" not in st.session_state or "last_update" not in st.session_state:
        update_data()  # 첫 번째 호출 시 데이터를 로드하여 세션에 저장
        st.session_state["last_update"] = datetime.now()
    else:
        current_time = datetime.now()
        if (current_time - st.session_state["last_update"]).seconds >= 60:  # 1분마다 갱신
            update_data()
            st.session_state["last_update"] = current_time


# 초기 화면 구성
st.title("🌾 엽채류 재배 의사결정시스템")
st.caption("맞춤형 농업 관리 도우미")

# 시스템에 따라 다른 폰트 적용
if platform.system() == 'Darwin':  # macOS
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':  # Windows
    rc('font', family='Malgun Gothic')
else:  # Linux, 기타
    rc('font', family='NanumGothic')

# # 한글 폰트 설정 (글씨 깨짐 방지)
# try:
#     font_url = "https://github.com/jumin7540/NanumFont/raw/master/NanumGothic.ttf"  # Nanum Gothic 폰트 URL
#     font_path = "/Users/sola/Documents/GitHub/2024_SAP/final/NanumGothic.ttf"  # 로컬 폰트 경로
#
#     # 폰트가 로컬에 없으면 다운로드
#     if not os.path.exists(font_path):
#         with open(font_path, "wb") as f:
#             f.write(requests.get(font_url).content)
#
#     # 폰트 설정
#     font = font_manager.FontProperties(fname=font_path).get_name()
#     rc('font', family=font)
#     st.success("한글 폰트가 성공적으로 설정되었습니다!")
# except Exception as e:
#     st.warning(f"폰트 설정 중 오류가 발생했습니다: {e}")


# 데이터 자동 갱신 함수 호출
auto_update()

# 사이드바 메뉴 설정
menu = st.sidebar.radio("메뉴를 선택하세요:", ["📘 사용법 안내", "📂 CSV 파일 관리", "📊 데이터 시각화", "📥 데이터 받기", "🌾 배추 생육 모델", "🌱 스팜이 챗봇", "📷 실시간 모니터링"])

# 메뉴에 따라 각 파일의 함수 실행
if menu == "📘 사용법 안내":
    dashboard_explanation.show()
elif menu == "📂 CSV 파일 관리":
    csv_management.show()
elif menu == "📊 데이터 시각화":
    data_visualization.show()
elif menu == "📥 데이터 받기":
    data_download.show()
elif menu == "🌾 배추 생육 모델":
    growth_model.show()
elif menu == "🌱 스팜이 챗봇":
    farm_chatbot.show()
elif menu == "📷 실시간 모니터링":
    rasp_camera.show()