FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]