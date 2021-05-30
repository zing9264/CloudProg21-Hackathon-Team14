FROM python:3.8-slim
ENV TZ=Asia/Taipei
ENV URL='0.0.0.0'
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
EXPOSE 5000
CMD ["python", "application.py"]