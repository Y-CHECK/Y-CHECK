# Python 3.10 slim 버전 사용
FROM python:3.10-slim

# 컨테이너 내부 작업 디렉토리
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Django 소스 복사
COPY . .

# Django 서버 실행 (개발용)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
