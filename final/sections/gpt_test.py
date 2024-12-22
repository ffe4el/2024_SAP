import streamlit as st
from openai import OpenAI

# OpenAI API 초기화
openai_api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)

# Streamlit 설정
st.title("PDF 기반 Chatbot")
st.write("업로드한 PDF 파일의 내용을 학습하여 질문에 답변합니다.")

# Step 1: PDF 파일 업로드
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요.", type=["pdf"])

if uploaded_file:
    st.write("파일 업로드 완료:", uploaded_file.name)

    # Step 2: Vector Store 생성 및 파일 업로드
    with st.spinner("PDF 파일을 처리 중입니다..."):
        try:
            # Vector Store 생성
            vector_store = client.beta.vector_stores.create(name="Farm Documents")

            # PDF 파일 스트림 준비
            file_stream = uploaded_file.getvalue()  # 업로드된 파일의 바이너리 데이터
            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=[file_stream],  # 여기서 file_stream만 전달
            )

            # Vector Store 상태 확인
            if file_batch.status == "completed":
                st.success("PDF 파일 처리 완료! 질문을 입력하세요.")
            else:
                st.error("파일 처리 중 문제가 발생했습니다.")
                st.stop()
        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.stop()

    # Step 3: 챗봇 기능 구현
    st.write("질문을 입력해 주세요:")
    user_input = st.text_input("질문 입력")

    if user_input:
        with st.spinner("질문 처리 중입니다..."):
            try:
                # Assistant 생성 및 Vector Store 연결
                assistant = client.beta.assistants.create(
                    name="Farm Chatbot Assistant",
                    instructions="You are an expert on farming-related documents. Use your knowledge base to answer questions.",
                    model="gpt-4o",
                    tools=[{"type": "file_search"}],
                    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
                )

                # 질문 처리
                thread = client.beta.threads.create(
                    messages=[{"role": "user", "content": user_input}],
                    assistant_id=assistant.id
                )
                response = client.beta.threads.runs.create(thread_id=thread.id)

                # 답변 출력
                st.write("**답변:**", response.result["messages"][0]["content"])
            except Exception as e:
                st.error(f"오류 발생: {e}")