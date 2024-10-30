import streamlit as st
import pandas as pd


def show():
    st.header("📂 CSV 파일 관리")
    data = st.session_state.get("data", pd.DataFrame())
    st.write("자동으로 데이터를 로드하고 있습니다. '데이터 시각화' 메뉴에서 데이터를 확인하세요.")

    if "log" in st.session_state:
        st.write("### 업데이트 로그")
        for log_entry in st.session_state["log"]:
            st.write(log_entry)
