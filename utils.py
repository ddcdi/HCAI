import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.messages import ChatMessage
import torch
import uuid
from gtts import gTTS
import sounddevice as sd
import wave
import speech_recognition as sr
from streamlit_extras.let_it_rain import rain

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 이전 대화 표시
def print_messages():
    if "messages" in st.session_state and len(st.session_state["messages"])>0 :
        for chat_message in st.session_state["messages"]:
            st.chat_message(chat_message.role).write(chat_message.content)

# 모델과 토크나이저 로드
def load_model():
    model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
    HUGGING_FACE_API_TOKEN = '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'

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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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


def messages_save():
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

def main_generate(prompt):
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


# ChatMessage 객체를 딕셔너리로 변환하는 함수
def chat_message_to_dict(chat_message):
    return {
        "role": chat_message.role,
        "content": chat_message.content
    }

def session_state_set():
    if "check" not in st.session_state:
        st.session_state.check = False

    if "started" not in st.session_state:
        st.session_state["started"] = False

    if "prompt" not in st.session_state:
        st.session_state.prompt = False

    if "select" not in st.session_state:
        st.session_state.select = False

    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

def language_convert(select_language):
    if select_language == "영어":
        return 'en'
    if select_language == "러시아어":
        return 'ru'
    if select_language == "중국어":
        # 중국어(간체)
        return 'zh-cn'
    if select_language == "일어":
        return 'ja'
    if select_language == "한국어":
        return 'ko'
    return False

def generate_audio(response,select_language):
    # 답변 음성 파일로 재생
    if st.button("오디오 생성"):
        text = response
        # 언어 설정
        if not language_convert(select_language):
            st.error("선택한 언어가 없습니댜.")
        language = language_convert(select_language)
        if text:
             # gTTS를 사용하여 텍스트를 오디오로 변환
            tts = gTTS(text=text, lang= language)
            audio_filename = st.session_state.session_id + ".mp3"
            tts.save(audio_filename)
                
            # 오디오 파일 재생
            audio_file = open(audio_filename, "rb")
            audio_bytes = audio_file.read()

            st.audio(audio_bytes, format="audio/wav")
        else:
            st.warning("재생할 동화가 없습니다.")


# 음성 녹음 함수 정의
def record_audio(duration=5, fs=44100, filename="output.wav"):
    # 사용 가능한 채널 수 확인
    device_info = sd.query_devices(kind='input')
    channels = device_info['max_input_channels']  # 사용 가능한 최대 입력 채널 수
    with st.spinner("녹음중입니다..."):
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='int16')
        sd.wait()  # 녹음이 끝날 때까지 대기
    
    # WAV 파일로 저장 (wave 모듈 사용)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16비트 오디오
        wf.setframerate(fs)
        wf.writeframes(recording.tobytes())
    
    st.success("녹음이 완료 되었습니다!")
    return filename

# 음성 인식 함수 정의
def recognize_speech(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)  # 전체 오디오 파일 읽기

    try:
        text = r.recognize_google(audio, language="ko-KR")
        return text
    except sr.UnknownValueError:
        st.write("음성을 인식하지 못했어요...")
        return None
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# 텍스트 파일에 저장하는 함수 정의
def save_text_to_file(text, filename="recognized_text.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    st.write(f"Text saved to {filename}")

# 이모지 rain 함수
def print_emoji(Emoji):
    rain(
        emoji=Emoji,
        font_size=54,
        falling_speed=5,
        animation_length="infinite",
    )
