import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.messages import ChatMessage
import torch
import uuid
from gtts import gTTS
import sounddevice as sd
import wave
import speech_recognition as sr
import urllib.request
import os
import re

# ChatMessage 객체를 딕셔너리로 변환하는 함수
def chat_message_to_dict(chat_message):
    return {
        "role": chat_message.role,
        "content": chat_message.content
    }

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

# text to speech 함수
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

# 이미지 생성 함수
def generate_image(word,client,setting):
  # 텍스트 프롬프트 설정
  prom_word = word + "in style of" + setting  # 생성할 이미지에 대한 설명

  # 이미지 생성 요청
  response = client.images.generate(
      model = "dall-e-3",
      prompt=prom_word,       # 텍스트 입력
      n=1,                    # 생성할 이미지 개수
      size="1024x1024"        # 이미지 크기
  )

  # 생성된 이미지의 URL 출력
  image_url = response.data[0].url

  # 세션 ID별 디렉토리 생성
  session_id = st.session_state.session_id  # Streamlit 세션 ID
  img_dest = f"images/{session_id}"  # 세션 ID 기반 저장 경로
  os.makedirs(img_dest, exist_ok=True)  # 디렉토리가 없으면 생성

  # 고유한 파일 이름 생성
  unique_id = str(uuid.uuid4())  # UUID로 고유 이름 생성
  file_path = os.path.join(img_dest, f"{unique_id}.jpg")  # 최종 파일 경로

  # 이미지 다운로드 및 저장
  urllib.request.urlretrieve(image_url, file_path)

  return image_url

# gpt 응답 저장
def save_gpt_response(gpt_response,text_storage):
    for page in gpt_response:
        # 빈 줄 건너뛰기
        if not page.strip():
            continue

        # 페이지 번호와 내용 분리
        if page.startswith("페이지"):
            parts = page.split(":", 1)
            if len(parts) > 1:
                page_num = parts[0]
                content = parts[1].strip()
                text_storage.append({"role": "assistant", "content": f"{page_num}: {content}"})
            else:
                print(f"Warning: Unexpected format in line: {page}")
        else:
            print(f"Warning: Line does not start with '페이지': {page}")

# 질문 확인 함수
def check_question_completion(gpt_response,complete,prefer_storage):
    # 응답 텍스트의 앞뒤 공백을 제거
    response = gpt_response.strip()

    # 답변에 중괄호가 들어가면 질문 완료
    if '{' in response and '}' in response:
        complete = True

        # 중괄호 안의 내용 추출
        match = re.search(r'\{(.*?)\}', response)
        if match:
            # 중괄호 안의 내용 선호도에 저장
            prefer_storage = match.group(1)
            print("결과:", st.session_state.parent_prefer)