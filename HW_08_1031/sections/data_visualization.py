import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.fetch_data import fetch_thingspeak_data

def calculate_vpd(temp, humid):
    es = 0.6108 * (17.27 * temp) / (temp + 237.3)
    vpd = (1 - humid / 100) * es
    return max(vpd, 0)

def calculate_dli(radn, light_hours=12):
    return radn * 3600 * light_hours / 1_000_000

def calculate_gdd(temp_max, temp_min, base_temp):
    return max(((temp_max + temp_min) / 2) - base_temp, 0)

def show():
    st.header("📊 데이터 시각화")

    # 기간 선택
    st.sidebar.subheader("기간 선택")
    start_date = st.sidebar.date_input("시작 날짜", datetime.now() - timedelta(days=7))
    end_date = st.sidebar.date_input("종료 날짜", datetime.now())

    # 집계 단위 선택
    st.sidebar.subheader("집계 단위 선택")
    avg_option = st.sidebar.selectbox("데이터 집계 단위", ["원본 데이터", "10분 평균", "1시간 평균", "하루 평균"])

    # GDD 기준 온도 입력 (집계 단위가 하루 평균일 때만 표시)
    base_temp = 10  # 기본값 설정
    if avg_option == "하루 평균":
        base_temp = st.sidebar.number_input("GDD 계산 기준 온도 (°C)", value=10)

    # 데이터 불러오기
    data = fetch_thingspeak_data(start_date, end_date)
    if data.empty:
        st.warning("선택한 기간 동안 데이터가 없습니다.")
        return

    # 데이터 집계 처리
    if avg_option == "10분 평균":
        data = data.resample('10T').mean()
    elif avg_option == "1시간 평균":
        data = data.resample('1H').mean()
    elif avg_option == "하루 평균":
        data = data.resample('D').mean()

    # 계산 컬럼 추가
    if avg_option == "원본 데이터":
        if 'temp' in data.columns and 'humid' in data.columns:
            data['VPD'] = data.apply(lambda row: calculate_vpd(row['temp'], row['humid']), axis=1)
    elif avg_option == "하루 평균":
        if 'radn' in data.columns:
            data['DLI'] = data['radn'].apply(lambda radn: calculate_dli(radn))
        if 'temp' in data.columns:
            data['GDD'] = data['temp'].apply(lambda temp: calculate_gdd(temp, temp, base_temp)).cumsum()

    # 시각화할 데이터 선택
    st.sidebar.subheader("시각화할 데이터를 선택하세요:")
    temp_checked = st.sidebar.checkbox("온도(℃)", value=True)
    humid_checked = st.sidebar.checkbox("습도(%)")
    radn_checked = st.sidebar.checkbox("일사량(W/㎡)")
    wind_checked = st.sidebar.checkbox("풍속(m/s)")
    rainfall_checked = st.sidebar.checkbox("강우량(mm)")
    battery_checked = st.sidebar.checkbox("배터리 전압(V)")
    vpd_checked = st.sidebar.checkbox("VPD (kPa)") if avg_option == "원본 데이터" else False
    gdd_checked = st.sidebar.checkbox("GDD (°C)") if avg_option == "하루 평균" else False
    dli_checked = st.sidebar.checkbox("DLI (mol/m²/day)") if avg_option == "하루 평균" else False

    # 그래프 구성
    fig = go.Figure()
    y_axis_label = []  # y축 레이블에 표시할 선택된 데이터

    # 각 데이터에 대해 선택된 항목을 기준으로 그래프에 추가
    if temp_checked and 'temp' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['temp'], mode='lines+markers', name="Temperature (℃)"))
        y_axis_label.append("Temperature (℃)")
    if humid_checked and 'humid' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['humid'], mode='lines+markers', name="Humidity (%)"))
        y_axis_label.append("Humidity (%)")
    if radn_checked and 'radn' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['radn'], mode='lines+markers', name="Radiation (W/㎡)"))
        y_axis_label.append("Radiation (W/㎡)")
    if wind_checked and 'wind' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['wind'], mode='lines+markers', name="Wind Speed (m/s)"))
        y_axis_label.append("Wind Speed (m/s)")
    if rainfall_checked and 'rainfall' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['rainfall'], mode='lines+markers', name="Rainfall (mm)"))
        y_axis_label.append("Rainfall (mm)")
    if battery_checked and 'battery' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['battery'], mode='lines+markers', name="Battery Voltage (V)"))
        y_axis_label.append("Battery Voltage (V)")
    if vpd_checked and 'VPD' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['VPD'], mode='lines+markers', name="VPD (kPa)"))
        y_axis_label.append("VPD (kPa)")
    if gdd_checked and 'GDD' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['GDD'], mode='lines+markers', name="GDD (°C)"))
        y_axis_label.append("GDD (°C)")
    if dli_checked and 'DLI' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['DLI'], mode='lines+markers', name="DLI (mol/m²/day)"))
        y_axis_label.append("DLI (mol/m²/day)")

    # y축 레이블 설정
    # fig.update_yaxes(title_text=", ".join(y_axis_label) if y_axis_label else "Values")
    fig.update_yaxes(title_text="")

    # x축 형식 설정 (날짜와 시간 함께 표시)
    fig.update_xaxes(
        title_text="Date (yy/mm/dd)",
        tickformat="%y/%m/%d<br>%H:%M"
    )

    # 그래프 레이아웃 설정
    fig.update_layout(
        title="환경 데이터 시각화",
        legend_title="데이터 종류",
        hovermode="x unified",
        showlegend=True
    )

    # 그래프 출력
    st.plotly_chart(fig)






