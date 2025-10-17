FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN flask --app app init-db

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "code.app:app"]
