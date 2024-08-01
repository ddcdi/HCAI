# 베이스 이미지 선택
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 컨테이너 실행 명령어
CMD ["streamlit", "run", "app.py"]
