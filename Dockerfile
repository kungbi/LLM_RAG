# FROM python:3.12.5-slim-bookworm
FROM --platform=linux/amd64 python:3.12.5-bookworm AS builder

# 시스템 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    gpg \
    build-essential \
    unixodbc-dev \
    libgssapi-krb5-2

# pip 업데이트 및 미러 서버 지정
RUN pip install --upgrade pip 

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --default-timeout=200 -r requirements.txt

# 최종 이미지
FROM --platform=linux/amd64 python:3.12.5-slim-bookworm

# 시스템 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    gpg \
    build-essential \
    unixodbc-dev \
    libgssapi-krb5-2

# 작업 디렉토리 설정
WORKDIR /app

# builder 스테이지에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 소스 코드 복사
COPY . .

# odbc-download.sh 실행
RUN chmod +x odbc-download.sh
RUN ./odbc-download.sh

# PATH 환경 변수 설정
ENV PATH="$PATH:/opt/mssql-tools/bin"

# 애플리케이션 실행
CMD ["streamlit", "run", "src/app.py"]
