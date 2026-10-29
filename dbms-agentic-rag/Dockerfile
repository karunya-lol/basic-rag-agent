# NoteWise AI — High-End Agentic RAG Platform Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
