import streamlit as st
import cv2
from PIL import Image
from io import BytesIO
import numpy as np

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
        try:
            # OpenCV를 사용해 스트림에서 프레임 캡처
            cap = cv2.VideoCapture(stream_url)
            ret, frame = cap.read()  # 첫 번째 프레임 읽기

            if ret:
                # OpenCV 이미지(Numpy 배열)를 PIL 이미지로 변환
                captured_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

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
            else:
                st.error("스트림에서 프레임을 읽을 수 없습니다.")
            cap.release()  # 스트림 해제
        except Exception as e:
            st.error(f"이미지 캡처 중 오류 발생: {e}")