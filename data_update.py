import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from io import StringIO

# ThingSpeak에서 월별 데이터 가져오기
def fetch_thingspeak_data(start_time, end_time):
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    url = f"https://api.thingspeak.com/channels/2328695/feeds.csv?start={start_str}&end={end_str}"
    response = requests.get(url)
    if response.status_code == 200:
        data = pd.read_csv(StringIO(response.text))

        # 열 이름을 원래 사용하던 데이터 형식에 맞추기
        data.columns = data.columns.str.lower().str.strip()
        data = data.rename(columns={
            "field1": "temp",  # 온도
            "field2": "humid",  # 습도
            "field3": "radn",  # 일사량
            "field4": "wind",  # 풍속
            "field5": "rainfall",  # 강우량
            "field6": "battery"  # 배터리 전압
        })

        # 이미 시간대가 있는지 확인 후 변환 처리
        data['created_at'] = pd.to_datetime(data['created_at'])
        if data['created_at'].dt.tz is None:
            data['created_at'] = data['created_at'].dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')
        else:
            data['created_at'] = data['created_at'].dt.tz_convert('Asia/Seoul')

        data = data.set_index('created_at')
        return data
    else:
        st.error("ThingSpeak 데이터 로딩 실패")
        return pd.DataFrame()

# 전체 데이터를 수집하여 저장하는 함수
def collect_data_from_start():
    start_date = datetime(2024, 1, 1)  # 시작 날짜를 2024년 1월 1일로 설정
    end_date = datetime.now()  # 현재 날짜까지

    # 월별로 데이터를 수집하여 합침
    all_data = pd.DataFrame()
    current_date = start_date
    while current_date < end_date:
        next_month = (current_date + timedelta(days=32)).replace(day=1)  # 다음 달 1일로 설정
        data = fetch_thingspeak_data(current_date, min(next_month, end_date))
        all_data = pd.concat([all_data, data])
        current_date = next_month

    return all_data

# 데이터를 주기적으로 갱신하는 함수
def update_data():
    data = collect_data_from_start()  # 2024년 1월 1일부터 현재까지의 데이터 수집

    # 로그 기록
    if "log" not in st.session_state:
        st.session_state["log"] = []
    st.session_state["log"].append(f"{datetime.now()} - 데이터 업데이트 완료")

    # 최신 데이터를 저장
    st.session_state["data"] = data

# GDD, VPD, DLI 계산 함수 정의
def calculate_vpd(temp, humid):
    humid = max(0, min(humid, 100))  # 습도는 0-100%로 제한
    es = 0.6108 * (17.27 * temp) / (temp + 237.3)  # 증기압 계산
    vpd = (1 - humid / 100) * es
    return max(vpd, 0)  # VPD는 음수가 될 수 없으므로 0 이하 값을 방지

def calculate_dli(ppfd, light_hours=12):
    return ppfd * 3600 * light_hours / 1_000_000  # 기본 단위: mol/m²/day

def calculate_gdd(temp_max, temp_min, base_temp):
    return max(((temp_max + temp_min) / 2) - base_temp, 0)

# 초기 화면 구성
st.title("전주 기상데이터 대시보드 🌱")

# 사이드바 메뉴
menu = st.sidebar.radio(
    "메뉴를 선택하세요:",
    ["📘 사용법 안내", "📂 CSV 파일 관리", "📊 데이터 시각화"],
)

# `update_data` 함수 호출하여 데이터 갱신
if "last_update" not in st.session_state:
    st.session_state["last_update"] = datetime.now() - timedelta(minutes=10)
current_time = datetime.now()
if (current_time - st.session_state["last_update"]).seconds >= 600:  # 10분 경과 확인
    update_data()
    st.session_state["last_update"] = current_time

# 메뉴에 따라 화면 출력
if menu == "📘 사용법 안내":
    st.header("📊 대시보드 설명")
    st.markdown("""
        본 대시보드는 전북대학교 학습도서관 4층 옥상에 설치된 AWS(Agricultural Weather Station)에서 수집된 데이터를 분석하고 시각화할 수 있습니다.
    """)

    # 설치 정보 및 수집 데이터 설명
    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 10px;">
    <h4>📍 설치 위치</h4>
    <p>- 위치: 전라북도 전주시 덕진구 백제대로 567 학습도서관 4층 옥상<br> - 좌표: 35.848°N, 127.136°E 🌱</p>
    </div>
    """, unsafe_allow_html=True)

    image_url = "https://i.imgur.com/GCtegFI.png"
    st.image(image_url, caption="전북대학교 학습도서관 AWS 설치 사진", use_column_width=True)

    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 10px;">
    <h4>📊 수집 데이터</h4>
    <ul>
        <li>온도: 섭씨 온도(℃)</li>
        <li>습도: 상대 습도(%)</li>
        <li>일사량: 일사(W/㎡)</li>
        <li>풍속: 1분평균풍속(m/s)</li>
        <li>강우량: 강우(mm)</li>
        <li>배터리 전압: 배터리 전압(V)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # 추가된 GDD, DLI, VPD 설명
    st.markdown("""
    <div style="background-color: #fff9c4; padding: 15px; border-radius: 10px;">
    <h4>📊 GDD, DLI, VPD 계산법</h4>
    <p>데이터 시각화에서 아래의 항목을 추가로 계산하여 분석할 수 있습니다:</p>
    <ul>
        <li><b>GDD (Growing Degree Days)</b>: GDD는 작물 성장에 유리한 온도를 기반으로 하는 지표입니다.</li>
        <p><b>공식</b>: (일최고기온 + 일최저기온) / 2 - 기준온도</p>
        <li><b>DLI (Daily Light Integral)</b>: DLI는 하루 동안 작물이 받은 총 광량을 나타냅니다.</li>
        <p><b>공식</b>: 일일광량(μmol/m²/s) × 3600 × 일광시간(시간) / 1,000,000</p>
        <li><b>VPD (Vapor Pressure Deficit)</b>: VPD는 공기 내 수증기량 부족을 나타내며, 작물 증산율에 영향을 줍니다.</li>
        <p><b>공식</b>: (1 - 상대습도/100) × 0.6108 × exp((17.27 × 온도) / (온도 + 237.3))</p>
    </ul>
    </div>
    """, unsafe_allow_html=True)

elif menu == "📂 CSV 파일 관리":
    st.header("📂 CSV 파일 관리")
    data = st.session_state.get("data", pd.DataFrame())
    st.write("자동으로 데이터를 로드하고 있습니다. '데이터 시각화' 메뉴에서 데이터를 확인하세요.")

    # 로그 표시
    if "log" in st.session_state:
        st.write("### 업데이트 로그")
        for log_entry in st.session_state["log"]:
            st.write(log_entry)

elif menu == "📊 데이터 시각화":
    st.header("📊 데이터 시각화")
    data = st.session_state.get("data", pd.DataFrame())

    if data.empty:
        st.write("데이터를 먼저 로드하세요.")
    else:
        # 사용자 지정 기간 설정
        min_date = data.index.min().date()
        max_date = data.index.max().date()
        start_date = st.sidebar.date_input("시작 날짜", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("종료 날짜", value=max_date, min_value=min_date, max_value=max_date)

        # 필터링 범위 적용
        start_datetime = pd.Timestamp(start_date).tz_localize("Asia/Seoul")
        end_datetime = pd.Timestamp(end_date).tz_localize("Asia/Seoul") + timedelta(days=1)
        filtered_data = data[(data.index >= start_datetime) & (data.index < end_datetime)]

        # 집계 단위 설정
        avg_option = st.sidebar.selectbox("데이터 집계 단위를 선택하세요:", ["원본 데이터(1분 간격)", "10분 평균", "1시간 평균", "하루 평균"])
        if avg_option == "10분 평균":
            filtered_data = filtered_data.resample('10T').mean()
        elif avg_option == "1시간 평균":
            filtered_data = filtered_data.resample('1H').mean()
        elif avg_option == "하루 평균":
            filtered_data = filtered_data.resample('D').mean()

        # GDD, DLI, VPD 계산
        base_temp = st.sidebar.number_input("GDD 계산 기준 온도 (°C)", value=10)
        filtered_data['VPD'] = filtered_data.apply(lambda row: calculate_vpd(row['temp'], row['humid']), axis=1)
        filtered_data['DLI'] = filtered_data['radn'].apply(
            lambda radn: calculate_dli(radn)) if 'radn' in filtered_data.columns else None
        filtered_data['GDD'] = filtered_data['temp'].apply(
            lambda temp: calculate_gdd(temp, temp, base_temp)).cumsum() if avg_option == "하루 평균" else None

        # 시각화 데이터 선택
        st.sidebar.markdown("### 시각화할 데이터를 선택하세요:")
        temp_checked = st.sidebar.checkbox("온도(℃)", value=True)
        humid_checked = st.sidebar.checkbox("습도(%)")
        radn_checked = st.sidebar.checkbox("일사(W/㎡)")
        wind_checked = st.sidebar.checkbox("1분평균풍속(m/s)")
        rainfall_checked = st.sidebar.checkbox("강우(mm)")
        battery_checked = st.sidebar.checkbox("배터리 전압(V)")
        vpd_checked = st.sidebar.checkbox("VPD (kPa)")
        gdd_checked = st.sidebar.checkbox("GDD (°C)") if avg_option == "하루 평균" else False
        dli_checked = st.sidebar.checkbox("DLI (mol/m²/s)") if avg_option == "하루 평균" else False

        # 그래프 구성
        fig = go.Figure()

        # 선택된 데이터만 그래프에 추가
        if temp_checked and 'temp' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['temp'], mode='lines', name="온도(℃)"))
        if humid_checked and 'humid' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['humid'], mode='lines', name="습도(%)"))
        if radn_checked and 'radn' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['radn'], mode='lines', name="일사(W/㎡)"))
        if wind_checked and 'wind' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['wind'], mode='lines', name="1분평균풍속(m/s)"))
        if rainfall_checked and 'rainfall' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['rainfall'], mode='lines', name="강우(mm)"))
        if battery_checked and 'battery' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['battery'], mode='lines', name="배터리 전압(V)"))
        if vpd_checked and 'VPD' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['VPD'], mode='lines', name="VPD (kPa)"))
        if gdd_checked and 'GDD' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['GDD'], mode='lines', name="GDD (°C)"))
        if dli_checked and 'DLI' in filtered_data.columns:
            fig.add_trace(
                go.Scatter(x=filtered_data.index, y=filtered_data['DLI'], mode='lines', name="DLI (mol/m²/s)"))

        # 그래프 레이아웃 설정
        fig.update_layout(
            title="환경 데이터 시각화",
            xaxis_title="시간",
            yaxis_title="값",
            legend_title="데이터 종류",
            hovermode="x",
            showlegend=True
        )

        # 그래프 출력
        st.plotly_chart(fig)

