import streamlit as st
from langchain_core.messages import ChatMessage
import json
import uuid
import utils
from gtts import gTTS

st.markdown("# Page 3 🎉")
st.markdown("hello")
messages = []

# 세션 상태 변수 초기화
if "check" not in st.session_state:
    st.session_state.check = False

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 메시지를 json 파일로 저장하는 버튼
if st.button("파일 저장하기"):
    st.session_state.check = True

if st.session_state.check :
    filename = st.session_state.session_id+".json"
    messages.append(ChatMessage(role="assistant",content="가나다라마바사아자차카타파하"))
    messages.append(ChatMessage(role="user",content="abcdefghijklmnopqustuvwxyz"))
    messages.append(ChatMessage(role="assistant",content="abcdefghijklmnopqustuvwxyz"))
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([utils.chat_message_to_dict(message) for message in messages], f, ensure_ascii=False, indent=4)
    st.success("성공적으로 파일을 저장했습니다!!")
    
    # 텍스트 입력받기
    text = st.text_input("텍스트를 입력하세요:")

    if st.button("오디오 생성"):
        if text:
            # gTTS를 사용하여 텍스트를 오디오로 변환
            tts = gTTS(text=text, lang='ko')  # 'ko'는 한국어
            tts.save("output.mp3")
            
            # 오디오 파일 재생
            audio_file = open("/Users/igwanhyeong/Desktop/.streamlit/output.mp3", "rb")
            audio_bytes = audio_file.read()

            st.audio(audio_bytes, format="audio/wav")
        else:
            st.warning("텍스트를 입력하세요.")

    # 다운로드 제공
    with open(filename, 'rb') as f:
        bytes_data = f.read()
    st.download_button(label="파일 다운로드", data=bytes_data, file_name=filename, mime='application/json')
    st.session_state.check = False


st.sidebar.markdown("# Page 3 🎉")