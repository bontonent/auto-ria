FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . . 

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p dumps

CMD ["python", "main.py"]
