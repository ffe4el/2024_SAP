import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
from io import StringIO

# 연도와 달에 맞는 데이터 자동 로딩 함수
@st.cache_data
def load_data(year, month):
    url = f"https://raw.githubusercontent.com/EthanSeok/JBNU_AWS/main/output/{year}_{month:02}.csv"
    response = requests.get(url)
    if response.status_code == 200:
        data = pd.read_csv(StringIO(response.text))
        data.columns = data.columns.str.lower().str.strip()
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data = data.set_index('timestamp')
        return data
    else:
        st.error("데이터 로딩 실패")
        return pd.DataFrame()

# 데이터 갱신 함수
def update_data_cache():
    current_year = datetime.now().year
    current_month = datetime.now().month
    all_data = pd.DataFrame()

    for month in range(1, current_month + 1):
        monthly_data = load_data(current_year, month)
        all_data = pd.concat([all_data, monthly_data])

    return all_data

# 초기 화면 구성
st.title("전주 기상데이터 대시보드 🌱")

# 사이드바 메뉴
menu = st.sidebar.radio(
    "메뉴를 선택하세요:",
    ["📘 사용법 안내", "📂 CSV 파일 관리", "📊 데이터 시각화"],
)

# 사용법 안내 메뉴
if menu == "📘 사용법 안내":
    st.header("📊 대시보드 설명")

    st.markdown("""
        본 대시보드는 전북대학교 학습도서관 4층 옥상에 설치된 AWS(Agricultural Weather Station)에서 수집된 데이터를 분석하고 시각화할 수 있습니다.\n
        아래는 주요 설치 정보와 수집 데이터에 대한 설명입니다.
    """)

    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 10px;">
    <h4>📍 설치 위치</h4>
    <p>- <b>위치</b>: 전라북도 전주시 덕진구 백제대로 567 학습도서관 4층 옥상<br>
    - <b>좌표</b>: 35.848°N, 127.136°E 🌱</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    image_url = "https://i.imgur.com/GCtegFI.png"
    st.image(image_url, caption="전북대학교 학습도서관 AWS 설치 사진", use_column_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 10px;">
    <h4>📅 데이터 수집 기간</h4>
    <p>- <b>기간</b>: 2024.1.1. ~ 진행중</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 10px;">
    <h4>📊 수집 데이터</h4>
    <ul>
        <li><b>온도</b>: 섭씨 온도(℃)</li>
        <li><b>습도</b>: 상대 습도(%)</li>
        <li><b>일사량</b>: 일사(W/㎡)</li>
        <li><b>풍향</b>: 풍향(degree)</li>
        <li><b>풍속</b>: 1분평균풍속(m/s)</li>
        <li><b>강우량</b>: 강우(mm)</li>
        <li><b>배터리전압</b>: 배터리 전압(V)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #ffe0e0; padding: 15px; border-radius: 10px;">
    <h4>📂 CSV 파일 관리</h4>
    <p>이 페이지에서는 데이터를 분석하기 위한 CSV 파일을 업로드할 수 있습니다. 올바른 CSV 파일의 형식은 다음과 같으며, <b>Timestamp</b> 열이 필수적으로 포함되어야 합니다.</p>
    <p>CSV 파일의 기본 형식 예시는 다음과 같습니다:</p>
    <table border="1" cellpadding="5" cellspacing="0">
    <tr><th>Timestamp</th><th>temp(℃)</th><th>humid(%)</th><th>radn(W/㎡)</th><th>wind(m/s)</th><th>rainfall(mm)</th><th>battery(V)</th></tr>
    <tr><td>2023-10-01 00:00</td><td>18.2</td><td>65</td><td>320</td><td>1.5</td><td>0</td><td>12.3</td></tr>
    <tr><td>2023-10-01 00:10</td><td>18.3</td><td>66</td><td>315</td><td>1.6</td><td>0</td><td>12.2</td></tr>
    </table>
    <p>이 형식을 유지한 상태로 CSV 파일을 업로드하면 데이터를 올바르게 시각화할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #fff9c4; padding: 15px; border-radius: 10px;">
    <h4>📊 데이터 시각화</h4>
    <p>CSV 파일이 성공적으로 업로드되면, 데이터를 시각화할 수 있는 페이지로 이동하여 다양한 설정을 할 수 있습니다.</p>
    <p>시각화 옵션:</p>
    <ul>
        <li><b>기간 설정</b>: 원하는 기간을 선택하여 특정 구간의 데이터를 확인할 수 있습니다.</li>
        <li><b>데이터 간격 설정</b>: 원본 데이터를 기준으로 10분, 1시간, 하루 평균으로 집계된 데이터를 확인할 수 있습니다.</li>
    </ul>

    <h5>GDD, DLI, VPD 계산법</h5>
    <p>데이터 시각화에서 아래의 항목을 추가로 계산하여 분석할 수 있습니다:</p>
    <ul>
        <li><b>GDD (Growing Degree Days)</b>: GDD는 작물 성장에 유리한 온도를 기반으로 하는 지표입니다.</li>
        <p><b>공식</b>: (일최고기온 + 일최저기온) / 2 - 기준온도</p>
        <li><b>DLI (Daily Light Integral)</b>: DLI는 하루 동안 작물이 받은 총 광량을 나타냅니다.</li>
        <p><b>공식</b>: 일일광량(μmol/m²/s) × 3600 × 일광시간(시간) / 1,000,000</p>
        <li><b>VPD (Vapor Pressure Deficit)</b>: VPD는 공기 내 수증기량 부족을 나타내며, 작물 증산율에 영향을 줍니다.</li>
        <p><b>공식</b>: (1 - 상대습도/100) × 0.6108 × exp((17.27 × 온도) / (온도 + 237.3))</p>
    </ul>
    <p>이 데이터를 활용하여 작물 성장에 필요한 기상 데이터를 분석할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)

elif menu == "📂 CSV 파일 관리":
    st.header("📂 CSV 파일 관리")
    data = update_data_cache()
    st.session_state["data"] = data
    st.write("자동으로 데이터를 로드하고 있습니다. '데이터 시각화' 메뉴에서 데이터를 확인하세요.")

elif menu == "📊 데이터 시각화":
    st.header("📊 데이터 시각화")
    if "data" not in st.session_state or st.session_state["data"].empty:
        st.write("데이터를 먼저 로드하세요.")
    else:
        data = st.session_state["data"]

        avg_option = st.sidebar.selectbox("데이터 집계 단위를 선택하세요:", ["원본 데이터(1분 간격)", "10분 평균", "1시간 평균", "하루 평균"])

        # 집계 단위 설정에 따른 데이터 처리
        if avg_option == "10분 평균":
            data = data.resample('10T').mean().dropna()
        elif avg_option == "1시간 평균":
            data = data.resample('1H').mean().dropna()
        elif avg_option == "하루 평균":
            data = data.resample('D').mean().dropna()

            # VPD, DLI, GDD 계산 함수 정의


        def calculate_vpd(temp, humid):
            humid = max(0, min(humid, 100))  # 습도는 0-100%로 제한
            es = 0.6108 * (17.27 * temp) / (temp + 237.3)  # 증기압 계산
            vpd = (1 - humid / 100) * es
            return max(vpd, 0)  # VPD는 음수가 될 수 없으므로 0 이하 값을 방지


        def calculate_dli(ppfd, light_hours=12):
            return ppfd * 3600 * light_hours / 1_000_000  # 기본 단위: mol/m²/day


        def calculate_gdd(temp_max, temp_min, base_temp):
            return max(((temp_max + temp_min) / 2) - base_temp, 0)

            # VPD는 모든 데이터 집계 단위에서 사용 가능


        data['VPD'] = data.apply(lambda row: calculate_vpd(row['temp'], row['humid']), axis=1)

        # 시각화 구간 선택
        start_date = st.sidebar.date_input("시작 날짜", value=data.index.min().date())
        end_date = st.sidebar.date_input("종료 날짜", value=data.index.max().date())
        filtered_data = data[(data.index >= pd.Timestamp(start_date)) & (data.index <= pd.Timestamp(end_date))]

        # GDD 및 DLI는 하루 평균에서만 계산
        if avg_option == "하루 평균":
            base_temp = st.sidebar.number_input("GDD 계산을 위한 기준 온도를 입력하세요 (°C)", value=10)
            filtered_data['DLI'] = filtered_data.apply(lambda row: calculate_dli(row['radn']), axis=1)
            filtered_data['GDD'] = filtered_data.apply(lambda row: calculate_gdd(row['temp'], row['temp'], base_temp),
                                                       axis=1).cumsum()

        # 시각화 데이터 선택
        st.sidebar.markdown("### 시각화할 데이터를 선택하세요:")
        temp_checked = st.sidebar.checkbox("온도(℃)", value=True)
        humid_checked = st.sidebar.checkbox("습도(%)")
        radn_checked = st.sidebar.checkbox("일사(W/㎡)")
        wind_checked = st.sidebar.checkbox("1분평균풍속(m/s)")
        rainfall_checked = st.sidebar.checkbox("강우(mm)")
        battery_checked = st.sidebar.checkbox("배터리 전압(V)")
        vpd_checked = st.sidebar.checkbox("VPD (kPa)")
        gdd_checked = dli_checked = False

        if avg_option == "하루 평균":
            gdd_checked = st.sidebar.checkbox("GDD (°C)")
            dli_checked = st.sidebar.checkbox("DLI (mol/m²/s)")

        # 선택된 데이터만 그래프에 추가
        fig = go.Figure()

        if temp_checked and 'temp' in data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['temp'], mode='lines', name="온도(℃)"))
        if humid_checked and 'humid' in data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['humid'], mode='lines', name="습도(%)"))
        if radn_checked and 'radn' in data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['radn'], mode='lines', name="일사(W/㎡)"))
        if wind_checked and 'wind' in data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['wind'], mode='lines', name="1분평균풍속(m/s)"))
        if rainfall_checked and 'rainfall' in data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['rainfall'], mode='lines', name="강우(mm)"))
        if battery_checked and 'battery' in data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['battery'], mode='lines', name="배터리 전압(V)"))
        if vpd_checked and 'VPD' in data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['VPD'], mode='lines', name="VPD (kPa)"))
        if gdd_checked and 'GDD' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['GDD'], mode='lines', name="GDD (°C)"))
        if dli_checked and 'DLI' in filtered_data.columns:
            fig.add_trace(
                go.Scatter(x=filtered_data.index, y=filtered_data['DLI'], mode='lines', name="DLI (mol/m²/s)"))

        fig.update_layout(
            title="환경 데이터 시각화",
            xaxis_title="시간",
            yaxis_title="값",
            legend_title="데이터 종류",
            hovermode="x",
            showlegend=True
        )
        st.plotly_chart(fig)

