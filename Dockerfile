FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8016

CMD ["gunicorn", "--bind", "0.0.0.0:8016", "--workers", "1", "app.main:app"]
