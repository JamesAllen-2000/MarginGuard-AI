# MarginGuard AI Services

This repository contains the intelligence microservice for MarginGuard AI built using FastAPI, designed for production environments and connected to Amazon Bedrock.

## Requirements

- Python 3.11+
- Docker (optional, for containerized run)

## Setup & Installation

### Option 1: Running Natively (Local Setup)

1. **Activate a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Environment:**
   Rename the `.env.example` file to `.env` (if not already done).
   Open the `.env` file and input your AWS keys to test the Amazon Bedrock Claude integration.
   
   ```env
   AWS_ACCESS_KEY_ID=AKIA_YOUR_ACTUAL_ACCESS_KEY
   AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_SECRET_KEY
   AWS_DEFAULT_REGION=us-east-1
   ```

### Option 2: Running via Docker (Production Deployment)

1. **Build the Container Image:**
   ```bash
   docker build -t marginguard-ai-service .
   ```

2. **Run the Container (mapping port 8000 and passing environment variables):**
   ```bash
   # If relying on .env file:
   docker run -p 8000:8000 --env-file .env marginguard-ai-service

   # Or passing keys explicitly:
   docker run -p 8000:8000 \
     -e AWS_ACCESS_KEY_ID=YOUR_KEY \
     -e AWS_SECRET_ACCESS_KEY=YOUR_SECRET \
     -e AWS_REGION=us-east-1 \
     marginguard-ai-service
   ```

## Starting the Application

If you elected to run natively on your machine, you have two options:

### Development Mode with Auto-Reload
For interacting with the API while coding:
```bash
uvicorn main:app --reload --port 8000
```

### Production Mode with Gunicorn
To test the clustered multi-worker environment:
```bash
gunicorn -c gunicorn_conf.py main:app
```

## Exploring the API

Once the app is running on Port `8000`, open your browser to view the **Interactive Swagger UI**:

🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

You can use the built-in Swagger UI to manually test:
- `POST /api/v1/risk-score`
- `POST /api/v1/explanation` (Connects to AWS Bedrock)
- `POST /api/v1/simulate`

## Testing

A comprehensive automated test covering simulation properties and limits has been configured natively via Pytest and Hypothesis.

To run tests:
```bash
python -m pytest tests -v
```
