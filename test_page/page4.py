import streamlit as st
from gtts import gTTS
import utils

# 텍스트 입력받기
text = st.text_input("텍스트를 입력하세요:")

utils.generate_audio(text,"한국어")