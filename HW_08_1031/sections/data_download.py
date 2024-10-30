import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
from utils.fetch_data import fetch_thingspeak_data  # 데이터 불러오는 함수


def show():
    st.title("데이터 받기")

    # 설명 텍스트
    st.markdown("""
    데이터를 다운로드하려면 기간을 선택하신 후 **"데이터 다운로드"** 버튼을 클릭하세요.
    선택한 기간 동안의 데이터를 CSV 파일로 데스크톱에 다운로드할 수 있습니다.
    """)

    # 장소 선택
    st.subheader("장소 선택")
    location = st.selectbox("장소를 선택하세요", ["전북대학교 학습도서관"])

    # 기간 선택
    st.subheader("기간 선택")
    start_date = st.date_input("시작 날짜", datetime.now() - timedelta(days=7))
    end_date = st.date_input("종료 날짜", datetime.now())


    # 데이터 다운로드 버튼
    if st.button("데이터 불러오기"):
        if start_date <= end_date:
            # 데이터 가져오기
            data = fetch_thingspeak_data(start_date, end_date)

            if not data.empty:
                # 데이터 다운로드 버튼 생성
                csv_buffer = StringIO()
                data.to_csv(csv_buffer, index=True)
                csv_data = csv_buffer.getvalue().encode('utf-8')

                st.download_button(
                    label="데이터 다운로드",
                    data=csv_data,
                    file_name=f"{location}_data_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
                st.success("데이터가 준비되었습니다. '데이터 다운로드' 버튼을 클릭하여 저장하세요.")
            else:
                st.error("선택한 기간 동안 데이터가 없습니다.")
        else:
            st.error("올바른 날짜 범위를 선택하세요.")




    #이거 나중에 이메일 전송 기능도 구현하면 좋을듯 지금은 그냥 기기에 바로 다운로드 되는 방향으로 구현
    # # 이메일 입력
    # st.subheader("이메일 주소")
    # email = st.text_input("이메일을 입력하세요")
    #
    #
    # # 다운로드 요청 버튼
    # if st.button("다운로드 요청"):
    #     if email and start_date <= end_date:
    #         # 여기에서 '전북대학교 학습도서관' 데이터를 API로 요청하는 로직을 추가할 수 있습니다.
    #         st.success(f"다운로드 요청이 접수되었습니다. {location} 데이터가 이메일로 전송됩니다.")
    #     else:
    #         st.error("올바른 이메일 주소와 날짜 범위를 입력하세요.")
