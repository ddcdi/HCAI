# 베이스 이미지 선택
FROM python:3.12.4

# 시스템 패키지 업데이트 및 portaudio와 관련 패키지 설치
RUN apt-get update \
        && apt-get install portaudio19-dev -y \
        && pip3 install pyaudio

RUN apt-get -y update
RUN apt-get -y upgrade

RUN pip install --upgrade pip

# 작업 디렉토리 설정
WORKDIR /app

# 필요 시, 필요한 다른 시스템 패키지 설치
# RUN apt-get install -y <other-packages>

# 필요한 Python 패키지 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 기본 명령어 설정 (예: Streamlit 애플리케이션 실행)
CMD ["streamlit", "run", "app.py"]
