FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (only if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Hugging Face requires port 7860
EXPOSE 7860

# Start FastAPI app
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]