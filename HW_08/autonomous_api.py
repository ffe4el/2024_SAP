import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.graph_objects as go

# 특정 연도의 CSV 파일을 weather_data 디렉토리에서 모두 읽는 함수
def load_csv_files_for_year(year):
    directory = './weather_data/'  # CSV 파일이 저장된 디렉토리
    data_frames = []
    months = set()  # 월을 저장할 집합

    # 디렉토리에서 파일 리스트 확인
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and filename.startswith(f"{year}_"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.lower().str.strip()  # 열 이름을 소문자 및 공백 제거
            if 'timestamp' not in df.columns:
                st.error(f"{filename} 파일에 'Timestamp' 열이 없습니다. 올바른 형식의 CSV 파일을 확인해주세요.")
                st.stop()
            df['timestamp'] = pd.to_datetime(df['timestamp'])  # Timestamp 열을 datetime으로 변환
            data_frames.append(df)

            # 파일명에서 월 추출 (예: '2024_09.csv'에서 '09' 추출)
            month = filename.split('_')[1].split('.')[0]
            months.add(month)

    if data_frames:
        # 모든 데이터프레임을 병합
        data = pd.concat(data_frames)
        data = data.sort_values(by='timestamp')  # Timestamp 기준으로 정렬
        data = data.set_index('timestamp')  # Timestamp를 인덱스로 설정
        return data, sorted(months)  # 데이터를 리턴할 때 월도 함께 리턴
    else:
        return None, None

# 초기 화면 구성
st.title("전주 기상데이터 대시보드 🌱")

# 사이드바 메뉴
menu = st.sidebar.radio(
    "메뉴를 선택하세요:",
    ["📘 사용법 안내", "📂 CSV 파일 관리", "📊 데이터 시각화"],
)

# 본문에 메뉴에 따라 내용 출력
if menu == "📘 사용법 안내":
    st.header("📊 대시보드 설명")

    st.markdown("""
        본 대시보드는 전북대학교 학습도서관 4층 옥상에 설치된 AWS(Agricultural Weather Station)에서 수집된 데이터를 분석하고 시각화할 수 있습니다.\n
        아래는 주요 설치 정보와 수집 데이터에 대한 설명입니다.
    """)

    # 설치 정보 섹션 - 파스텔톤 배경 추가 및 이미지 삽입
    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 10px;">
    <h4>📍 설치 위치</h4>
    <p>- <b>위치</b>: 전라북도 전주시 덕진구 백제대로 567 학습도서관 4층 옥상<br>
    - <b>좌표</b>: 35.848°N, 127.136°E 🌱</p>
    </div>
    """, unsafe_allow_html=True)

    # 섹션 간 간격 추가
    st.markdown("<br>", unsafe_allow_html=True)

    # Imgur 이미지 URL 적용
    image_url = "https://i.imgur.com/GCtegFI.png"
    st.image(image_url, caption="전북대학교 학습도서관 AWS 설치 사진", use_column_width=True)

    # 섹션 간 간격 추가
    st.markdown("<br>", unsafe_allow_html=True)

    # 데이터 수집 기간 섹션 - 파스텔톤 배경 추가
    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 10px;">
    <h4>📅 데이터 수집 기간</h4>
    <p>- <b>기간</b>: 2023.9.1. ~ 진행중</p>
    </div>
    """, unsafe_allow_html=True)

    # 섹션 간 간격 추가
    st.markdown("<br>", unsafe_allow_html=True)

    # 수집 데이터 설명 섹션 - 파스텔톤 배경 추가
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

    # 섹션 간 간격 추가
    st.markdown("<br>", unsafe_allow_html=True)

    # CSV 파일 관리에 대한 설명 - 빨간색 파스텔 톤
    st.markdown("""
    <div style="background-color: #ffe0e0; padding: 15px; border-radius: 10px;">
    <h4>📂 CSV 파일 관리</h4>
    
    <p>GitHub Actions는 사용자가 코드를 커밋하지 않아도, 매 2시간마다 설정된 Python 스크립트를 자동으로 실행합니다. <br> 이 스크립트는 기상 데이터를 수집하고 해당 연도의 CSV 파일에 데이터를 추가합니다. 사용자는 업데이트된 데이터를 바로 확인할 수 있습니다.</p>

    <h5>GitHub Actions 참고 코드</h5>
    <p>GitHub Actions는 다음과 같이 설정됩니다:</p>
    <ol>
      <li>`.github/workflows/` 디렉토리에 워크플로우 파일을 추가합니다.</li>
      <li> 워크플로우는 <b>매 2시간</b>마다 데이터를 자동으로 업데이트 됩니다.</li>
    </ol>

    ``` yaml
        name: Update Weather Data
    
        on:
          schedule:
            - cron: '0 */2 * * *'  # 매 2시간마다 실행
    
        jobs:
          update-weather-data:
            runs-on: ubuntu-latest
    
            steps:
            - name: Checkout repository
              uses: actions/checkout@v2  # 저장소에서 코드를 가져옵니다.
    
            - name: Set up Python
              uses: actions/setup-python@v2
              with:
                python-version: '3.x'  # Python 환경 설정
    
            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip
                pip install requests pandas  # 필요한 패키지 설치
    
            - name: Run Python script
              run: |
                python get_data.py  # 데이터를 자동으로 불러오는 Python 스크립트 실행
    
            - name: Commit and push changes
              run: |
                git config --global user.name "Your Name"
                git config --global user.email "your-email@example.com"
                git add weather_data/*.csv
                git commit -m "Auto update weather data"
                git push
              env:
                GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # GitHub 푸시를 위한 인증 토큰 
    ```
            
    <h5>CSV 파일 형식</h5>
    <p>각 파일은 다음과 같은 형식을 유지하며, <b>Timestamp</b> 열이 필수적으로 포함 됩니다.</p>
    <p>CSV 파일 형식은 아래와 같습니다 : </p>
    <table border="1" cellpadding="5" cellspacing="0">
    <tr><th>Timestamp</th><th>temp(℃)</th><th>humid(%)</th><th>radn(W/㎡)</th><th>wind(m/s)</th><th>rainfall(mm)</th><th>battery(V)</th></tr>
    <tr><td>2023-10-01 00:00</td><td>18.2</td><td>65</td><td>320</td><td>1.5</td><td>0</td><td>12.3</td></tr>
    <tr><td>2023-10-01 00:10</td><td>18.3</td><td>66</td><td>315</td><td>1.6</td><td>0</td><td>12.2</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

    # 섹션 간 간격 추가
    st.markdown("<br>", unsafe_allow_html=True)

    # 데이터 시각화에 대한 설명 - 노란색 파스텔 톤
    st.markdown("""
    <div style="background-color: #fff9c4; padding: 15px; border-radius: 10px;">
    <h4>📊 데이터 시각화</h4>
    <p>CSV 파일을 성공적으로 불러오면, 데이터를 시각화할 수 있는 페이지로 이동하여 다양한 설정을 할 수 있습니다.</p>
    <p>시각화 옵션:</p>
    <ul>
        <li><b>기간 설정</b>: 원하는 기간을 선택하여 특정 구간의 데이터를 확인할 수 있습니다.</li>
        <li><b>데이터 간격 설정</b>: 원본 데이터를 기준으로 10분, 1시간, 하루 평균으로 집계된 데이터를 확인할 수 있습니다.</li>
    </ul

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

if menu == "📂 CSV 파일 관리":
    st.header("📂 CSV 파일 관리")
    year = st.number_input("확인할 연도를 입력하세요", min_value=2000, max_value=datetime.now().year, step=1)

    # 해당 연도의 CSV 파일 읽기
    if year:
        data, months = load_csv_files_for_year(year)
        if data is not None:
            st.session_state["data"] = data  # 데이터를 session_state에 저장
            months_str = ', '.join(months)  # 월들을 문자열로 변환
            st.write(f"{year}년의 {months_str}월 데이터가 성공적으로 업로드되었습니다. '데이터 시각화' 메뉴에서 데이터를 확인하세요.")
        else:
            st.write(f"{year}년의 데이터를 찾을 수 없습니다.")
    else:
        st.write("연도를 입력하세요.")

elif menu == "📊 데이터 시각화":
    st.header("📊 데이터 시각화")
    if "data" not in st.session_state:
        st.write("CSV 파일을 먼저 업로드하세요.")
    else:
        data = st.session_state["data"]  # session_state에서 데이터 가져오기

        avg_option = st.sidebar.selectbox("데이터 집계 단위를 선택하세요:", ["원본 데이터(1분 간격)", "10분 평균", "1시간 평균", "하루 평균"])

        # 하루 평균을 선택했을 때만 기준 온도 입력란이 보이도록 설정
        if avg_option == "하루 평균":
            base_temp = st.sidebar.number_input("GDD 계산을 위한 기준 온도를 입력하세요 (°C)", value=10)
        else:
            base_temp = None

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

        # VPD 및 DLI는 모든 데이터 집계 단위에서 사용 가능
        data['VPD'] = data.apply(lambda row: calculate_vpd(row['temp'], row['humid']), axis=1)

        # GDD 및 DLI는 하루 평균에서만 계산
        if avg_option == "하루 평균":
            data['DLI'] = data.apply(lambda row: calculate_dli(row['radn']), axis=1)
            data['GDD'] = data.apply(lambda row: calculate_gdd(row['temp'], row['temp'], base_temp), axis=1).cumsum()

        start_date = st.sidebar.date_input("시작 날짜", value=data.index.min().date())
        end_date = st.sidebar.date_input("종료 날짜", value=data.index.max().date())
        filtered_data = data[(data.index >= pd.Timestamp(start_date)) & (data.index <= pd.Timestamp(end_date))]

        # 체크박스로 시각화할 데이터 선택
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

        selected_traces = 0
        first_axis_name = ""
        second_axis_name = ""

        if temp_checked and 'temp' in data.columns:
            selected_traces += 1
            yaxis = "y1" if selected_traces == 1 else "y2"
            if selected_traces == 1:
                first_axis_name = "온도(℃)"
            elif selected_traces == 2:
                second_axis_name = "온도(℃)"
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['temp'], mode='lines', name="온도(℃)", yaxis=yaxis))

            if avg_option == "하루 평균":
                st.write(f"### 온도 통계")
                st.write(f"평균: {filtered_data['temp'].mean():.2f}℃, 최대: {filtered_data['temp'].max():.2f}℃, 최소: {filtered_data['temp'].min():.2f}℃")

        if humid_checked and 'humid' in data.columns:
            selected_traces += 1
            yaxis = "y1" if selected_traces == 1 else "y2"
            if selected_traces == 1:
                first_axis_name = "습도(%)"
            elif selected_traces == 2:
                second_axis_name = "습도(%)"
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['humid'], mode='lines', name="습도(%)", yaxis=yaxis))

            if avg_option == "하루 평균":
                st.write(f"### 습도 통계")
                st.write(f"평균: {filtered_data['humid'].mean():.2f}%, 최대: {filtered_data['humid'].max():.2f}%, 최소: {filtered_data['humid'].min():.2f}%")

        if radn_checked and 'radn' in data.columns:
            selected_traces += 1
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['radn'], mode='lines', name="일사(W/㎡)"))

        if wind_checked and 'wind' in data.columns:
            selected_traces += 1
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['wind'], mode='lines', name="1분평균풍속(m/s)"))

        if rainfall_checked and 'rainfall' in data.columns:
            selected_traces += 1
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['rainfall'], mode='lines', name="강우(mm)"))

        if battery_checked and 'battery' in data.columns:
            selected_traces += 1
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['battery'], mode='lines', name="배터리 전압(V)"))

        # VPD는 음수가 나올 수 없으므로 최소값을 0으로 설정
        if vpd_checked and 'VPD' in data.columns:
            selected_traces += 1
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['VPD'], mode='lines', name="VPD (kPa)", yaxis="y1"))
            fig.update_yaxes(rangemode="tozero", title_text="VPD (kPa)")

        if gdd_checked and 'GDD' in data.columns:
            selected_traces += 1
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['GDD'], mode='lines', name="GDD (°C)"))

        if dli_checked and 'DLI' in data.columns:
            selected_traces += 1
            fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['DLI'], mode='lines', name="DLI (mol/m²/s)"))

        # 그래프 레이아웃에 x축과 y축의 단위 추가 및 Y축 범위 설정
        fig.update_layout(
            title="환경 데이터 시각화",
            xaxis_title="시간",
            yaxis=dict(title=first_axis_name, titlefont=dict(color="black")),  # Y축 글자 색을 검정으로 통일
            yaxis2=dict(title=second_axis_name, overlaying="y", side="right", titlefont=dict(color="black")),
            legend_title="데이터 종류",
            hovermode="x",
            showlegend=True
        )
        st.plotly_chart(fig)
