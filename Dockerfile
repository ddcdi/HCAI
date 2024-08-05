# 베이스 이미지 선택
FROM python:3.11-slim

# 필요한 패키지 업데이트 및 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    file \
    git \
    portaudio19-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# pip를 통한 pyaudio 설치
RUN pip install --upgrade pip
RUN pip install streamlit pyaudio

# Streamlit 설정 디렉토리 생성 및 설정 파일 복사
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY main_page.py .
COPY utils.py .
COPY page/ ./page

# 기본 명령어 설정 (예: Streamlit 애플리케이션 실행)
CMD ["streamlit", "run", "main_page.py"]




