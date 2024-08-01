import streamlit as st
import utils
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.messages import ChatMessage
import json
from gtts import gTTS
import sounddevice as sd
import wave
import speech_recognition as sr

st.title("동화만들기 🎈")
st.markdown("원하는 주제로 동화를 작성해주는 AI")

# 언어 설정
select_language = st.sidebar.selectbox(
    "이중 언어 설정",
    ("영어","러시아어","중국어","일어")
)

print(select_language)

# 세션 상태 변수 초기화
utils.session_state_set()

print("세션 ID : ",st.session_state.session_id)

prompt = ""

# 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

topic = st.selectbox(
    "주제를 골라봐",
    ["과일","캐릭터","동물"],
    placeholder="원하는 주제 선택하기",
    index= None
)

if (topic=="과일"):
    if st.button("버튼을 누르고 말해보세요",help="사과,바나나,수박..."):
        audio_file = utils.record_audio()
        text = utils.recognize_speech(audio_file)
        st.session_state.prompt = text
        print(f"프롬프트 : {prompt}")
elif (topic=="캐릭터"):
    prompt = st.text_input('원하는 캐릭터를 작성해봐',placeholder = '뽀로로,또봇,미미...')
elif (topic=="동물"):
    prompt = st.text_input('원하는 동물을 작성해봐',placeholder ='강아지,고양이,토끼...')
    
if prompt:
    st.session_state.prompt = True

if st.session_state.prompt:
    if st.button("시작", type="primary"):
        st.session_state["started"] = True

if st.session_state["started"]:
    
    # 이전 대화 저장 및 출력
    utils.messages_save()

    # 질문 받기
    if st.session_state.prompt and not st.session_state.select:
        user_input = st.session_state.prompt
        print(f"user_input : {user_input}")
        user_message = ChatMessage(role="user", content=user_input)
        st.session_state["messages"].append(user_message)
        
        with st.chat_message("user"):
            st.write(user_input)

        # 모델 불러오기
        with st.spinner("열심히 동화를 만들고 있는중..."):
            if "tokenizer" not in st.session_state or "model" not in st.session_state:
                try:
                    st.session_state["tokenizer"], st.session_state["model"] = utils.load_model()
                except Exception as e:
                    st.error(f"모델을 불러오는 중 오류가 발생했습니다: {e}")
                    st.stop()
        
        # 답변 생성
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = utils.generate_text(
                        user_input, st.session_state["tokenizer"], st.session_state["model"]
                    )
                    st.markdown(response)
                except Exception as e:
                    st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
                    st.stop()
        
        assistant_message = ChatMessage(role="assistant", content=response)
        st.session_state["messages"].append(assistant_message)
        st.session_state.select = True
    
    # 이미 주제를 선택했을때
    elif st.session_state.prompt:
        user_input = st.chat_input("원하신걸 말씀해보세요")

        user_message = ChatMessage(role="user", content=user_input)
        st.session_state["messages"].append(user_message)
        
        with st.chat_message("user"):
            st.write(user_input)

        # 모델 불러오기
        with st.spinner("열심히 동화를 만들고 있는중..."):
            if "tokenizer" not in st.session_state or "model" not in st.session_state:
                try:
                    st.session_state["tokenizer"], st.session_state["model"] = utils.load_model()
                except Exception as e:
                    st.error(f"모델을 불러오는 중 오류가 발생했습니다: {e}")
                    st.stop()
        
        # 답변 생성
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = utils.generate_text(
                        user_input, st.session_state["tokenizer"], st.session_state["model"]
                    )
                    st.markdown(response)
                    
                    # 답변 음성 파일로 재생
                    utils.generate_audio(response,select_language)
                except Exception as e:
                    st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
                    st.stop()
                
        
        assistant_message = ChatMessage(role="assistant", content=response)
        st.session_state["messages"].append(assistant_message)

    # 메시지를 json 파일로 저장하는 버튼
    if st.button("종료"):
        st.session_state.check = True

    if st.session_state.check :
        filename = st.session_state.session_id+".json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([utils.chat_message_to_dict(message) for message in st.session_state["messages"]], f, ensure_ascii=False, indent=4)
        st.success("성공적으로 종료했습니다!!")

else:
    st.markdown("작성을 완료하고 시작 버튼을 눌러주세요")
