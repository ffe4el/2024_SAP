import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta


def show():
    st.header("📊 데이터 시각화")
    data = st.session_state.get("data", pd.DataFrame())

    if data.empty:
        st.write("데이터가 로드되지 않았습니다.")
    else:
        min_date = data.index.min().date()
        max_date = data.index.max().date()

        # 사용자 지정 기간 설정
        start_date = st.sidebar.date_input("시작 날짜", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("종료 날짜", value=max_date, min_value=min_date, max_value=max_date)

        # date_input으로 선택한 날짜를 datetime으로 변환하고 시간대 설정
        start_datetime = pd.Timestamp(start_date).tz_localize("Asia/Seoul")
        end_datetime = pd.Timestamp(end_date).tz_localize("Asia/Seoul") + timedelta(days=1)

        # 필터링 범위 적용
        filtered_data = data[(data.index >= start_datetime) & (data.index < end_datetime)]

        # 집계 단위 선택 옵션
        st.sidebar.markdown("### 데이터 집계 단위를 선택하세요:")
        aggregation_option = st.sidebar.selectbox("집계 단위", ["원본 데이터", "10분 평균", "1시간 평균", "하루 평균"])

        # 데이터 집계 처리
        if aggregation_option == "10분 평균":
            filtered_data = filtered_data.resample('10T').mean()
        elif aggregation_option == "1시간 평균":
            filtered_data = filtered_data.resample('1H').mean()
        elif aggregation_option == "하루 평균":
            filtered_data = filtered_data.resample('D').mean()

        # 시각화할 데이터 선택 옵션
        st.sidebar.markdown("### 시각화할 데이터를 선택하세요:")
        temp_checked = st.sidebar.checkbox("온도(℃)", value=True)
        humid_checked = st.sidebar.checkbox("습도(%)")
        radn_checked = st.sidebar.checkbox("일사(W/㎡)")
        wind_checked = st.sidebar.checkbox("풍속(m/s)")
        rainfall_checked = st.sidebar.checkbox("강우(mm)")
        battery_checked = st.sidebar.checkbox("배터리 전압(V)")

        # 시간별 데이터를 그래프로 표시
        fig = go.Figure()

        # 선택된 데이터만 그래프에 추가 (점 + 선 모드, connectgaps=True로 선 연결)
        if temp_checked and 'temp' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data.index, y=filtered_data['temp'], mode='lines+markers', name="온도(℃)",
                marker=dict(size=4),  # 점의 크기 조정
                connectgaps=True  # 결측치 구간을 연결
            ))
        if humid_checked and 'humid' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data.index, y=filtered_data['humid'], mode='lines+markers', name="습도(%)",
                marker=dict(size=4),
                connectgaps=True
            ))
        if radn_checked and 'radn' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data.index, y=filtered_data['radn'], mode='lines+markers', name="일사(W/㎡)",
                marker=dict(size=4),
                connectgaps=True
            ))
        if wind_checked and 'wind' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data.index, y=filtered_data['wind'], mode='lines+markers', name="풍속(m/s)",
                marker=dict(size=4),
                connectgaps=True
            ))
        if rainfall_checked and 'rainfall' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data.index, y=filtered_data['rainfall'], mode='lines+markers', name="강우(mm)",
                marker=dict(size=4),
                connectgaps=True
            ))
        if battery_checked and 'battery' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data.index, y=filtered_data['battery'], mode='lines+markers', name="배터리 전압(V)",
                marker=dict(size=4),
                connectgaps=True
            ))

        # 그래프 레이아웃 설정
        fig.update_layout(
            title="환경 데이터 시각화",
            xaxis_title="시간",
            yaxis_title="값",
            legend_title="데이터 종류",
            hovermode="x",
            showlegend=True
        )

        # 첫 번째 그래프 출력 (시간별 데이터)
        st.plotly_chart(fig)
