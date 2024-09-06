import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.messages import ChatMessage
import torch

# Hugging Face API 토큰
HUGGING_FACE_API_TOKEN = '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'

model_name = "meta-llama/Meta-Llama-3-8B-Instruct"

# 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# 모델과 토크나이저 로드
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        use_auth_token=HUGGING_FACE_API_TOKEN
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        use_auth_token=HUGGING_FACE_API_TOKEN
    ).to(device)
    return tokenizer, model

# 텍스트 생성 함수
def generate_text(prompt, tokenizer, model):
    # 입력 텍스트 토크나이즈
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    print("입력 텍스트:", inputs)  # 디버깅을 위해 입력 텍스트 출력
    try:
        outputs = model.generate(
            **inputs,
            max_length=50,  # 출력 시퀀스의 최대 길이
            num_return_sequences=1,  # 생성할 시퀀스 수
            no_repeat_ngram_size=2,  # 반복되지 않을 n-그램 크기
            do_sample=True,  # 샘플링 활성화
            top_k=50,  # 상위 k개의 토큰만 고려
            top_p=0.95  # 누적 확률이 0.95 이하인 토큰만 고려
        )
        print("모델 출력:", outputs)  # 디버깅을 위해 모델 출력 텍스트 출력
        # 출력 디코딩
        response = tokenizer.decode(outputs[0].cpu(), skip_special_tokens=True)
        st.write("Response:")
        st.write(response)
        return response
    except Exception as e:
        print(f"모델 응답 생성 중 오류 발생: {e}")
        return "응답을 생성하는데 실패했습니다."


def main_generate():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 이전 대화 표시
    for message in st.session_state["messages"]:
        with st.chat_message(message.role):
            st.write(message.content)

    # 질문 받기
    if prompt := st.chat_input("원하는 주제를 말해보세요"):
        user_message = ChatMessage(role="user", content=prompt)
        st.session_state["messages"].append(user_message)
        
        with st.chat_message("user"):
            st.write(prompt)

        # 모델 불러오기
        if "tokenizer" not in st.session_state or "model" not in st.session_state:
            st.session_state["tokenizer"], st.session_state["model"] = load_model()
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_text(
                    prompt,st.session_state["tokenizer"],st.session_state["model"]
                )
                st.markdown(response)
        
        assistant_message = ChatMessage(role= "assistant", content=response)
        st.session_state["messages"].append(assistant_message)