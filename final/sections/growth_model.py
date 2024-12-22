import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
from io import StringIO
import matplotlib.pyplot as plt


# ThingSpeak에서 데이터 가져오기 함수
def fetch_thingspeak_data(start_time, end_time):
    API_KEY = "YOUR_API_KEY_HERE"
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    url = f"https://api.thingspeak.com/channels/2328695/feeds.csv?start={start_str}&end={end_str}&api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = pd.read_csv(StringIO(response.text))
        data.columns = data.columns.str.lower().str.strip()
        data = data.rename(columns={
            "field1": "temp",  # 온도
            "field3": "radn",  # 일사량
        })

        # created_at 열 변환
        data['created_at'] = pd.to_datetime(data['created_at'])
        if data['created_at'].dt.tz is None:
            data['created_at'] = data['created_at'].dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')
        else:
            data['created_at'] = data['created_at'].dt.tz_convert('Asia/Seoul')

        data = data.set_index('created_at')

        # 필요한 열만 선택
        data = data[['temp', 'radn']]

        # 일사량(W/m²)을 MJ/m²로 변환
        interval_seconds = 3600  # 1시간 간격 데이터로 가정
        data['radn'] = data['radn'] * interval_seconds / 1_000_000  # W/m² -> MJ/m² 변환

        return data
    else:
        print(f"데이터 로드 실패: {response.status_code}")
        return pd.DataFrame()


# RUE 계산 함수
def calculate_rue(temp):
    if temp < 5:
        return 0
    elif 5 <= temp < 15:
        return 0.0004 * temp + 1.2114
    elif 15 <= temp < 25:
        return 0.0599 * temp + 0.3553
    elif 25 <= temp < 35:
        return -0.0373 * temp + 2.6765
    else:
        return 0


# 생체중 변화율 계산 함수
def calculate_biomass_change(rue, radn, lai=3, extinction_coefficient=0.35):
    f_solar = 1 - np.exp(-extinction_coefficient * lai)
    return rue * radn * f_solar / 1000  # g을 kg으로 변환


def display_summary(data, area, total_production, total_income):
    # 선택한 기간 출력
    st.write("### 📝 결과 요약")
    period_start = data.index.min().date()
    period_end = data.index.max().date()
    cumulative_biomass = data['biomass_change'].sum()

    # 결과 카드 형식으로 출력
    st.markdown(
        f"""
        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
            <h4 style="color: #2d89ef;">📅 선택한 기간:</h4>
            <p style="font-size: 18px;"><strong>{period_start} - {period_end}</strong></p>
            <h4 style="color: #44c767;">🌱 누적 생체중 변화량:</h4>
            <p style="font-size: 18px; color: #2e7d32;"><strong>{cumulative_biomass:.2f} kg/m²</strong></p>
            <h4 style="color: #0078d7;">🌾 총 생산량:</h4>
            <p style="font-size: 18px; color: #005a9e;"><strong>{total_production:.2f} kg</strong> (재배 면적: {area:.1f} m² 기준)</p>
            <h4 style="color: #d83b01;">💰 총 예상 수익:</h4>
            <p style="font-size: 20px; color: #d83b01;"><strong>{total_income:,.0f} 원</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 농넷 링크 추가
    st.markdown(
        "[🌐 농넷 가격 정보 확인하기 ✅](https://www.nongnet.or.kr/front/M000000006/stats/totSearch2.do?keyword=1001)"
    )


# 생체중 변화량을 하루 단위로 집계하고 막대그래프로 시각화
def plot_daily_cumulative_biomass(data, area):
    # 날짜별로 그룹화하여 누적 생체중 계산
    data['date'] = data.index.date
    daily_cumulative = data.groupby('date')['biomass_change'].sum().cumsum()

    # 막대그래프 시각화
    st.write("### 일별 누적 생체중 변화량 (kg):")
    fig, ax = plt.subplots()
    daily_cumulative.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title("Daily Cumulative Biomass Change")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Biomass (kg/m²)")
    ax.set_xticks(range(0, len(daily_cumulative), max(1, len(daily_cumulative) // 10)))  # Adjust x-axis tick spacing
    ax.set_xticklabels([str(x) for x in daily_cumulative.index[::max(1, len(daily_cumulative) // 10)]], rotation=45)
    st.pyplot(fig)

    # 누적 생체중 변화량 및 총 생산량/수익 계산
    cumulative_biomass = data['biomass_change'].sum()
    total_production = cumulative_biomass * area
    price_per_10kg = 12148  # 10kg당 가격
    total_income = total_production * (price_per_10kg / 10)  # 총 수익 계산 (kg 기준)

    # 결과 요약 표시
    display_summary(data, area, total_production, total_income)


# Streamlit UI
def show():
    st.title("베타함수 기반 작물 생육 모델")

    # 📘 프로젝트 개요 섹션
    with st.expander("📘 프로젝트 개요"):
        st.markdown("""
        본 프로젝트는 **GDD(일적산온도) 모델**의 한계를 극복하기 위해 **베타함수 기반 온도 모델**과
        **광 이용효율(RUE)**을 활용하여 작물 생육을 더 정확히 예측하는 것을 목표로 합니다.
        RUE는 전북대학교 AWS에서 제공하는 **온도**와 **일사량** 데이터를 기반으로 계산되었습니다.
        """)

    # 💡 GDD와 베타함수 비교 섹션
    with st.expander("💡 GDD와 베타함수 비교"):
        st.markdown("""
        **GDD 모델의 한계**
        1. 온도와 생육 간의 **선형적 관계**만 가정.
        2. **최적 온도 및 온도 한계**를 명확히 설정하지 못함.
        3. **고온 스트레스**에 의한 생육 감소를 반영하지 못함.

        **베타함수의 장점**
        1. 온도와 생육 속도 간의 **비선형적 관계** 반영.
        2. **최적 온도에서 최대 생육 속도**를 명확히 표현.
        3. 고온 스트레스에 따른 생육 감소 반영.
        """)

    # 📈 RUE 기반 생체중 변화량 계산 섹션
    with st.expander("📈 RUE 기반 생체중 변화량 계산"):
        st.markdown("""
        RUE는 다음과 같은 수식을 기반으로 생체중 변화량을 계산합니다:
        """)
        st.latex(r"""
        \frac{dW}{dt} = \epsilon \cdot I_0 \cdot f_{solar}
        """)
        st.markdown("""
        - \( \epsilon \): RUE (g/MJ)
        - \( I_0 \): 일사량 (W/m²)
        - \( f_{solar} \): 광 흡수 비율 (엽면적 지수와 관련)

        RUE는 온도 구간별로 달라지며, 아래의 구간별 회귀식으로 계산됩니다.
        """)

    # 📊 온도 구간별 RUE 회귀식 섹션
    with st.expander("📊 온도 구간별 RUE 회귀식"):
        st.table({
            "온도 구간 (°C)": ["temp < 5", "5 ≤ temp < 15", "15 ≤ temp < 25", "25 ≤ temp < 35", "temp ≥ 35"],
            "RUE 회귀식": [
                "0",
                "0.0004x + 1.2114",
                "0.0599x + 0.3553",
                "-0.0373x + 2.6765",
                "0"
            ]
        })

    # 🔍 베타함수를 활용한 생육 모델링 섹션
    with st.expander("🔍 베타함수를 활용한 생육 모델링"):
        st.markdown("""
        - 최적 온도: 약 24°C
        - 생육 최저 온도: 5°C
        - 생육 최고 온도: 35°C

        베타함수 기반 RUE를 사용하여 온도와 생체중 변화량 간의 비선형적 관계를 시뮬레이션할 수 있습니다.
        """)

    # 🚀 프로젝트 목표 섹션
    with st.expander("🚀 프로젝트 목표"):
        st.markdown("""
        1. 온도와 광 이용효율을 고려한 현실적 <b>생육 모델 개발</b>
        2. 전북대학교 AWS 기상 데이터를 활용한 <b>생체중 변화량 계산</b>
        3. 기존 모델(GDD) 대비 <b>정확한 생육 예측</b> 제공
        """)

    # 데이터 가져오기 섹션
    st.header("환경 데이터 입력 및 결과 분석")
    start_date = st.date_input("재배 시작 날짜", value=datetime.now() - timedelta(days=7))
    end_date = st.date_input("재배 종료 날짜", value=datetime.now())

    # 재배 면적 입력
    st.title("베타함수 기반 작물 생육 모델")

    # 면적 입력
    area_input = st.number_input(
        "재배 면적 입력 (m²):",
        min_value=1.0,
        step=0.1,
        value=10000.0,  # 초기값 설정
    )

    st.write(f"현재 입력된 재배 면적: **{area_input:.1f} m²**")

    if st.button("환경 데이터 가져오기"):
        data = fetch_thingspeak_data(start_date, end_date)
        if not data.empty:
            st.write("### 가져온 데이터:")
            st.write(data)

            # RUE 계산
            data['rue'] = data['temp'].apply(calculate_rue)

            # 생체중 변화 계산
            data['biomass_change'] = data.apply(
                lambda row: calculate_biomass_change(row['rue'], row['radn']), axis=1
            )

            # 누적 생체중 변화량 시각화
            plot_daily_cumulative_biomass(data, area_input)
