import json
import time
import streamlit as st
import openai

# OpenAI API 초기화
openai_api_key = st.secrets["openai"]["api_key"]
openai.api_key = openai_api_key

ASSISTANT_ID = st.secrets["openai"]["assistant_id"]


# thread 새로 발급
def create_new_thread():
    thread = openai.beta.threads.create()
    return thread


def summit_message(assistant_id, thread_id, user_message):
    # thread 에 메세지 전송
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # Run을 실행시켜 Assistant 와 연결
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    return run


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def get_response(thread_id):
    return openai.beta.threads.messages.list(thread_id=thread_id, order="asc")


def print_message(response):
    for res in response:
        print(f"[res.role.upper()]\n{res.content[0].text.value}\n")


def show_json(obj):
    print(json.load(obj.model_dump_json()))


def main():
    THREAD_ID = create_new_thread().id

    USER_MESSAGE = "지금은 4월 1일인데, 상추 재배하는 방법에 대해서 자세하게 알려줘"

    run = summit_message(ASSISTANT_ID, THREAD_ID, USER_MESSAGE)

    run1 = wait_on_run(run, THREAD_ID)

    print_message(get_response(THREAD_ID).data[-2:])


if __name__ == "__main__":
    main()