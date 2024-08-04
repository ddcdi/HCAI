# 베이스 이미지 선택
FROM python:3.12.4

# 필요한 패키지 업데이트 및 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    file \
    git \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Homebrew 사용자 생성 및 홈 디렉토리 설정
RUN useradd -m -s /bin/bash brewuser

# brewuser로 전환
USER brewuser
WORKDIR /home/brewuser

# Homebrew 설치
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Homebrew 환경 변수 설정
ENV PATH="/home/brewuser/.linuxbrew/bin:/home/brewuser/.linuxbrew/sbin:${PATH}"

# Homebrew 업데이트 및 필수 패키지 설치
RUN brew update && brew install portaudio

# 루트 사용자로 전환
USER root

# pip를 통한 pyaudio 설치
RUN pip install pyaudio

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 기본 명령어 설정 (예: Streamlit 애플리케이션 실행)
CMD ["streamlit", "run", "app.py"]

