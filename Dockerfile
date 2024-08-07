# Python 이미지 사용
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 소스 복사
COPY . /app/

# 포트 설정
EXPOSE 8000

# 서버 실행 명령
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000 --settings=onestep_be.settings.prod"]
