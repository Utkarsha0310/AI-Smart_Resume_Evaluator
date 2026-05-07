FROM python:3.12-slim

# Install Java Runtime (required by language_tool_python)
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre-headless && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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

# Single worker to fit in 512MB RAM (Render free tier)
# Increased timeout for NLP analysis (grammar check can take 30-60s)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--threads", "2", "--timeout", "180", "app:app"]
