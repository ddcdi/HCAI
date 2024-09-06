import streamlit as st
from PIL import Image
import numpy as np

# 여기에 생성형 AI 모델을 불러오고 이미지를 생성하는 코드 추가
def generate_image():
    # 예시로 랜덤 이미지 생성 (실제 모델 대신)
    return np.random.rand(100, 100, 3) * 255

st.title("생성형 AI 이미지 출력")
st.markdown(1)
if st.button("이미지 생성"):
    img_array = generate_image()
    img = Image.fromarray(img_array.astype('uint8'))
    st.image(img, caption='생성된 이미지', use_column_width=True)