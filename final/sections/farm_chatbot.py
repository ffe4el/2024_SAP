import streamlit as st
import openai
import time
import re

# OpenAI API 초기화
openai_api_key = st.secrets["openai"]["api_key"]
openai.api_key = openai_api_key
ASSISTANT_ID = st.secrets["openai"]["assistant_id"]

# 소스 표시 제거 함수
def clean_response(response):
    """
    응답에서 【숫자:숫자†source】 형태의 불필요한 출처 표시를 제거하는 함수
    """
    cleaned_response = re.sub(r'【\d+:\d+†?source?】', '', response)
    return cleaned_response.strip()

# OpenAI Thread 처리 함수
def create_new_thread():
    return openai.beta.threads.create().id

def submit_message(assistant_id, thread_id, user_message):
    openai.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_message
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )
    return run

def wait_on_run(run, thread_id):
    while run.status in ["queued", "in_progress"]:
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run.id
        )
        time.sleep(0.5)
    return run

def get_response(thread_id):
    return openai.beta.threads.messages.list(thread_id=thread_id, order="asc")


def show():
    # Streamlit 설정
    st.title("🌱 스마트팜 재배 도우미")
    st.caption("작물 관리, 병해충 대처, 재배 일정 관리까지 한눈에 확인하세요!")

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "안녕하세요! 스마트팜 재배 도우미 🌱스팜이🌱입니다. 무엇을 도와드릴까요?"}
        ]

    # 기존 메시지 출력
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # 버튼에 따른 예시 질문 표시
    st.subheader("🧑‍🌾 궁금한 내용을 선택하세요!")

    if st.button("🌿 병해충 해결법"):
        example_question = "배추 잎이 노랗게 변하고 있어요. 어떻게 해야 하나요?"
        st.info(f"**예시 질문:** {example_question}")

    if st.button("📅 재배 일정 관리"):
        example_question = "4월 10일에 상추를 심었어요. 수확은 언제 할 수 있나요?"
        st.info(f"**예시 질문:** {example_question}")

    if st.button("🌱 작물별 재배 가이드"):
        example_question = "시금치 재배 시 중요한 관리 사항을 알려주세요."
        st.info(f"**예시 질문:** {example_question}")

    if st.button("📝 재배 기록 관리"):
        example_question = "상추 재배 보고서를 어떻게 작성해야 하나요?"
        st.info(f"**예시 질문:** {example_question}")

    # 사용자 입력 처리
    if prompt := st.chat_input("궁금한 점을 입력하세요!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # OpenAI API 호출
        THREAD_ID = create_new_thread()
        run = submit_message(ASSISTANT_ID, THREAD_ID, prompt)
        run = wait_on_run(run, THREAD_ID)

        # 응답 처리
        response = get_response(THREAD_ID).data[-2:]
        assistant_response = response[-1].content[0].text.value
        cleaned_response = clean_response(assistant_response)  # 출처 제거

        # 결과 출력
        st.session_state.messages.append({"role": "assistant", "content": cleaned_response})
        st.chat_message("assistant").write(cleaned_response)