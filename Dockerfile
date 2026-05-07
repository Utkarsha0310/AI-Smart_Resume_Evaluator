FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads reports data

EXPOSE 10000

# --preload: loads app ONCE before forking workers (spaCy model shared in memory)
# 1 worker + 2 threads: fits in Render free tier (512MB RAM)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--threads", "2", "--timeout", "120", "--preload", "app:app"]
