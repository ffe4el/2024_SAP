import streamlit as st


def show():
    st.header("📊 대시보드 설명")
    st.markdown("""
        본 대시보드는 전북대학교 학습도서관 4층 옥상에 설치된 AWS(Agricultural Weather Station)에서 수집된 데이터를 분석하고 시각화할 수 있습니다.
    """)

    # 설치 위치와 설명
    st.markdown("""
    <div class="card">
        <div class="section-title">📍 설치 위치</div>
        <p>- 위치: 전라북도 전주시 덕진구 백제대로 567 학습도서관 4층 옥상<br> - 좌표: 35.848°N, 127.136°E 🌱</p>
    </div>
    """, unsafe_allow_html=True)

    st.image("https://i.imgur.com/GCtegFI.png", caption="전북대학교 학습도서관 AWS 설치 사진", use_column_width=True)

    # 수집 데이터 설명
    st.markdown("""
    <div class="card">
        <div class="section-title">📊 수집 데이터</div>
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

    # 섹션 간 간격 추가
    st.markdown("<br>", unsafe_allow_html=True)

    # CSV 파일 관리에 대한 설명 - 빨간색 파스텔 톤
    st.markdown("""
        <div style="background-color: #ffe0e0; padding: 15px; border-radius: 10px;">
        <h4>📂 CSV 파일 관리</h4>

        <p>GitHub Actions는 사용자가 코드를 커밋하지 않아도, 10분마다 설정된 Python 스크립트를 자동으로 실행합니다. <br> 이 스크립트는 기상 데이터를 수집하고 해당 연도의 CSV 파일에 데이터를 추가합니다. 사용자는 업데이트된 데이터를 바로 확인할 수 있습니다.</p>

        <h5>GitHub Actions 참고 코드</h5>
        <p>GitHub Actions는 다음과 같이 설정됩니다:</p>
        <ol>
          <li>`.github/workflows/` 디렉토리에 워크플로우 파일을 추가합니다.</li>
          <li> 워크플로우는 <b>10 분</b>마다 데이터를 자동으로 업데이트 됩니다.</li>
        </ol>

        ``` yaml
            name: Update Weather Data

            on:
              schedule:
                - cron: '*/10 * * * *'  # 매 10분마다 실행

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
                    python ./HW_08/get_data.py  # 상대 경로로 수정
                  env:
                    MY_GITHUB_TOKEN: ${{ secrets.SOLA_GITHUB_TOKEN }}
            
                - name: Commit and push changes
                  run: |
                    git config --global user.name "ffe4el"
                    git config --global user.email "codkan20@gmail.com"
                    git add weather_data/*  # 상대 경로로 수정
                    git commit -m "Update Weather Data - $(TZ='Asia/Seoul' date +'%Y-%m-%d')"
                    git push
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
            <li><b>GDD (Growing Degree Days)</b>: GDD는 작물 성장에 유리한 온도를 기반으로 하는 지표입니다. </li>
            <p><b>공식</b>: (일최고기온 + 일최저기온) / 2 - 기준온도</p>
            <li><b>DLI (Daily Light Integral)</b>: DLI는 하루 동안 작물이 받은 총 광량을 나타냅니다.</li>
            <p><b>공식</b>: 일일광량(μmol/m²/s) × 3600 × 일광시간(시간) / 1,000,000</p>
            <li><b>VPD (Vapor Pressure Deficit)</b>: VPD는 공기 내 수증기량 부족을 나타내며, 작물 증산율에 영향을 줍니다.</li>
            <p><b>공식</b>: (1 - 상대습도/100) × 0.6108 × exp((17.27 × 온도) / (온도 + 237.3))</p>
        </ul>
        <p>이 데이터를 활용하여 작물 성장에 필요한 기상 데이터를 분석할 수 있습니다.</p>

        <이번 과제에서 가정>
        <ul>
            <li>GDD 누적 온도는 편의상 10월1일부터 누적 시킵니다. </li>
            <li>청경채의 생육적온 : 20~25℃, GDD 기준 온도(생육 한계 온도) : 4.4 ℃, GDD 가 400 ℃ 누적되었을때 수확 적정 시기</li>
            <li>고랭지배추의 생육적온 : 15~20℃, GDD 기준 온도(생육 한계 온도) : 5.0 ℃, GDD 가 900 ℃ 누적되었을때 수확 적정 시기</li>
        </ul>    

        </div>
        """, unsafe_allow_html=True)
