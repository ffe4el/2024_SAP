import streamlit as st
import requests
from PIL import Image
from io import BytesIO


def show():
    # Streamlit 페이지 제목
    st.title("농부를 위한 실시간 카메라 도구")
    st.write("실시간 스트림에서 사진을 캡처하고 다운로드할 수 있습니다.")

    # 실시간 스트림 URL
    stream_url = "http://113.198.63.27:30350/monitor"

    # iframe으로 실시간 스트림 표시
    st.markdown(
        f"""
        <iframe src="{stream_url}" width="1280" height="720" frameborder="0" allowfullscreen></iframe>
        """,
        unsafe_allow_html=True
    )

    # 사진 찍기 버튼
    if st.button("📸 사진 찍기"):
        # 스트림 URL에서 현재 프레임 캡처
        try:
            response = requests.get(stream_url, stream=True)
            response.raise_for_status()  # 요청 상태 확인

            # 이미지 데이터를 읽어서 PIL Image로 변환
            img_bytes = BytesIO(response.content)
            captured_image = Image.open(img_bytes)

            # 캡처된 이미지 표시
            st.image(captured_image, caption="캡처된 이미지", use_column_width=True)

            # 이미지 다운로드 버튼
            buf = BytesIO()
            captured_image.save(buf, format="JPEG")
            buf.seek(0)
            st.download_button(
                label="⬇️ 이미지 다운로드",
                data=buf,
                file_name="captured_image.jpg",
                mime="image/jpeg"
            )
        except Exception as e:
            st.error(f"이미지 캡처 중 오류 발생: {e}")
