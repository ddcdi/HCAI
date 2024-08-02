# 베이스 이미지 선택
FROM python:3.12.4

# portaudio 설치
RUN apt-get update && apt-get install -y portaudio19-dev

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정 (기본 포트 설정)
ENV PORT=8501

# 컨테이너 실행 명령어
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
