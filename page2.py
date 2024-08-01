import streamlit as st
import sounddevice as sd
import wave
import speech_recognition as sr

# 사용 가능한 채널 수 확인
device_info = sd.query_devices(kind='input')
channels = device_info['max_input_channels']  # 사용 가능한 최대 입력 채널 수

# 음성 녹음 함수 정의
def record_audio(duration=5, fs=44100, filename="output.wav"):
    st.write("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='int16')
    sd.wait()  # 녹음이 끝날 때까지 대기
    
    # WAV 파일로 저장 (wave 모듈 사용)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16비트 오디오
        wf.setframerate(fs)
        wf.writeframes(recording.tobytes())
    
    st.write("Recording complete.")
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
        st.write("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# 텍스트 파일에 저장하는 함수 정의
def save_text_to_file(text, filename="recognized_text.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    st.write(f"Text saved to {filename}")

# Streamlit 앱 설정
st.title("Speech Recognition and Save to Text File")

if st.button("Start Speech Recognition"):
    audio_file = record_audio()
    text = recognize_speech(audio_file)
    if text:
        st.write(f"Recognized Text: {text}")
        save_text_to_file(text)
