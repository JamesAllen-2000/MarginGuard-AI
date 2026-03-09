# MarginGuard AI Services

MarginGuard AI is an intelligence microservice built with **FastAPI** that calculates risk scores, generates AI explanations via **Amazon Bedrock (Claude)**, and simulates the financial impact of price changes for e-commerce SKUs.

## 🚀 Core Features

1. **Risk Engine**: Analyzes key SKU metrics (Margin Trend, Ad Efficiency, Fee Impact, Return Rate) and assigns a composite risk score between 0 and 100.
2. **AI Explanations**: Uses AWS Bedrock to generate human-readable insights explaining why a specific SKU is at risk and what actions can help stabilize margins.
3. **Price Simulation**: Simulates the effect of price changes on volume, revenue, and margins using demand elasticity models (-0.8 elasticity), and recalculates the risk score based on the new metrics.

## 🏗️ Architecture & Project Structure

The project strictly follows a layered microservice architecture:

```text
.
├── api/                  # API routing layer
│   └── routers/
│       ├── intelligence.py # Primary endpoints (Risk, AI, Simulate)
│       └── raw_data.py     # Generic ingestion routes
├── core/                 # Core business logic
│   ├── config.py         # Environment configurations
│   ├── risk_engine.py    # Multi-factor risk scoring algorithms
│   └── simulator.py      # Demand elasticity and price modeling
├── models/               # Data Layer
│   └── schemas.py        # Pydantic models for strict I/O validation
├── services/             # External Integrations
│   ├── bedrock_client.py   # AWS Bedrock/Claude integration
│   ├── prompts.py          # AI prompt templates
│   └── supabase_client.py  # Database connection handling
├── tests/                # Pytest suit covering physics & limits
├── main.py               # FastAPI application entry point
└── requirements.txt      # Project dependencies
```

## 📋 Requirements

- Python 3.11+
- AWS Account (for Bedrock access)
- Docker (optional, for containerization)

## 🛠️ Setup & Installation

### Option 1: Running Natively (Local Setup)

1. **Clone the repository and activate a Virtual Environment:**
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
   Rename `.env.example` to `.env`. Open the file and configure your AWS credentials to enable live Bedrock AI explanations (otherwise, the app safely falls back to mock responses).

   ```env
   # .env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
   ```

### Option 2: Running via Docker (Production)

1. **Build the Container Image:**
   ```bash
   docker build -t marginguard-ai-service .
   ```

2. **Run the Container:**
   ```bash
   docker run -p 8000:8000 --env-file .env marginguard-ai-service
   ```

## ⚡ Starting the Application

**Development Mode (Auto-Reloading):**
```bash
uvicorn main:app --reload --port 8000
```

**Production Mode (Multi-Worker):**
```bash
gunicorn -c gunicorn_conf.py main:app
```

## 🔌 Exploring the API

Once the server is running, you can explore and interact with the API via the built-in Swagger interface at:

🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

### Primary Endpoints:
- `POST /api/v1/risk-score`
  - *Returns the 0-100 risk score based on current SKU data.*
- `POST /api/v1/explanation`
  - *Calls AWS Bedrock to provide an AI analysis of the current risk.*
- `POST /api/v1/simulate`
  - *Pass `newPrice` and the SKU object to see the projected elasticity impact and updated risk score.*

## 🧪 Testing

The repository uses `pytest` alongside `hypothesis` to fuzz test the simulation properties, volume elasticity, and limit handling.

Run tests with:
```bash
python -m pytest tests -v
```
