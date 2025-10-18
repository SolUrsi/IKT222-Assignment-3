FROM python:3.10-slim

# Necessary for dos2unix to force Unix line endings to allows execution of entrypoint script in Linux environment
RUN apt-get update && apt-get install -y dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .
COPY .env .

COPY entrypoint.sh /usr/local/bin/
RUN dos2unix /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["entrypoint.sh"]