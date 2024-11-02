# import streamlit as st
# from datetime import datetime, timedelta
# from sections import dashboard_explanation, csv_management, data_visualization
# from utils.fetch_data import fetch_thingspeak_data
#
#
# # CSS 파일 불러오기
# def load_css(file_path):
#     with open(file_path) as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#
#
# # 메인 CSS 로드
# load_css("css/style.css")
#
#
# # 데이터 업데이트 함수
# def update_data():
#     # 최근 일주일치 데이터를 가져오는 예시
#     start_date = datetime.now() - timedelta(days=7)
#     end_date = datetime.now()
#     data = fetch_thingspeak_data(start_date, end_date)
#     st.session_state["data"] = data  # 데이터를 세션 상태에 저장
#
#     # 로그 기록을 위해 세션 상태에 로그 초기화 및 추가
#     if "log" not in st.session_state:
#         st.session_state["log"] = []
#     st.session_state["log"].append(f"{datetime.now()} - 데이터 업데이트 완료")
#
#
# # 1분마다 자동으로 데이터 업데이트 설정
# def auto_update():
#     if "data" not in st.session_state or "last_update" not in st.session_state:
#         update_data()  # 첫 번째 호출 시 데이터를 로드하여 세션에 저장
#         st.session_state["last_update"] = datetime.now()
#     else:
#         current_time = datetime.now()
#         if (current_time - st.session_state["last_update"]).seconds >= 60:  # 1분마다 갱신
#             update_data()
#             st.session_state["last_update"] = current_time
#
#
# # 초기 화면 구성
# st.title("전주 기상데이터 대시보드 🌱")
#
# # 데이터 자동 갱신 함수 호출
# auto_update()
#
# # 사이드바 메뉴 설정
# menu = st.sidebar.radio("메뉴를 선택하세요:", ["📘 사용법 안내", "📂 CSV 파일 관리", "📊 데이터 시각화"])
#
# # 메뉴에 따라 각 파일의 함수 실행
# if menu == "📘 사용법 안내":
#     dashboard_explanation.show()
# elif menu == "📂 CSV 파일 관리":
#     csv_management.show()
# elif menu == "📊 데이터 시각화":
#     data_visualization.show()

import streamlit as st
from datetime import datetime, timedelta
from sections import dashboard_explanation, csv_management, data_visualization, data_download
from utils.fetch_data import fetch_thingspeak_data

# # CSS 파일 불러오기
# def load_css(file_path):
#     with open(file_path) as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#
# # 메인 CSS 로드
# load_css("css/style.css")

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
st.title("전주 기상데이터 대시보드 🌱")

# 데이터 자동 갱신 함수 호출
auto_update()

# 사이드바 메뉴 설정
menu = st.sidebar.radio("메뉴를 선택하세요:", ["📘 사용법 안내", "📂 CSV 파일 관리", "📊 데이터 시각화", "📥 데이터 받기"])

# 메뉴에 따라 각 파일의 함수 실행
if menu == "📘 사용법 안내":
    dashboard_explanation.show()
elif menu == "📂 CSV 파일 관리":
    csv_management.show()
elif menu == "📊 데이터 시각화":
    data_visualization.show()
elif menu == "📥 데이터 받기":
    data_download.show()  # data_download.py의 show() 함수 호출
