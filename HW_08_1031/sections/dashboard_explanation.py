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

    # GDD, DLI, VPD 설명
    st.markdown("""
    <div class="highlight">
        <div class="section-title">📊 GDD, DLI, VPD 계산법</div>
        <p>데이터 시각화에서 아래의 항목을 추가로 계산하여 분석할 수 있습니다:</p>
        <ul>
            <li><b>GDD (Growing Degree Days)</b>: (일최고기온 + 일최저기온) / 2 - 기준온도</li>
            <li><b>DLI (Daily Light Integral)</b>: 일일광량(μmol/m²/s) × 3600 × 일광시간 / 1,000,000</li>
            <li><b>VPD (Vapor Pressure Deficit)</b>: (1 - 상대습도/100) × 0.6108 × exp((17.27 × 온도) / (온도 + 237.3))</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
