FROM python:3.10-slim

WORKDIR /app

COPY capture_images_and_send.py .

RUN pip install requests

CMD ["python", "capture_images_and_send.py"]
