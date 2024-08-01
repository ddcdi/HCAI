# 베이스 이미지 선택
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요에 따라 시스템 종속성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 파일을 컨테이너에 복사
COPY requirements.txt .

# requirements.txt에 있는 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 컨테이너 실행 명령어
CMD ["streamlit", "run", "app.py"]
