FROM python:3.11-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PYTHONPATH=/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

