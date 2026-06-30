FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

COPY requirements_pinned.txt .

RUN pip install --no-cache-dir -r requirements_pinned.txt

COPY app/pathway_server.py /app/app/pathway_server.py
COPY app/pipeline2.py /app/app/pipeline2.py

COPY data/result.csv /app/data/result.csv

EXPOSE 8003

CMD ["python", "app/pathway_server.py"]