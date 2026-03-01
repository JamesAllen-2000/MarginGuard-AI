# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies if required (mostly for pandas/numpy or native extensions, skipping here for pure fastAPI)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port (Internal mapping for ECS/K8s/ALB)
EXPOSE 8000

# Start command utilizing the configured Gunicorn layer 
CMD ["gunicorn", "-c", "gunicorn_conf.py", "main:app"]
