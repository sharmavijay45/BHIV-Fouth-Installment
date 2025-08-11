### BHIV Core - Third Installment

An advanced multi-modal AI pipeline with reinforcement learning, knowledge-base retrieval (NAS + FAISS + file retriever), a production-ready FastAPI layer, web interface, and an enhanced CLI.

### Key Features
- Multi-modal processing: text, PDF, image, audio
- Knowledge-aware responses: NAS/File-based retrieval with FAISS fallback
- Reinforcement learning: adaptive agent/model selection with logging and analytics
- Web UI: authenticated uploads, dashboard, and downloads
- CLI: single/batch processing with JSON/Text/CSV output
- Health, metrics, MongoDB logging, and retry/error handling

### Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   CLI Runner    │    │  Simple API     │
│   (Port 8003)   │    │  (Enhanced)     │    │  (Port 8001)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └──────────────┬────────┴──────────────┬────────┘
                        │                       │
                   ┌───────────────┐       ┌───────────────┐
                   │  MCP Bridge   │       │  Knowledge KB │
                   │  (Port 8002)  │       │  (NAS/FAISS)  │
                   └───────────────┘       └───────────────┘
                              │
                 ┌────────────┴────────────┐
                 │  Agent Registry + RL    │
                 │  (text/pdf/image/audio) │
                 └──────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Optional: MongoDB 5.0+ for logging/analytics
- Optional: Docker for vector DBs/services

### Install
```bash
git clone <repository-url>
cd BHIV-Third-Installment
python -m venv .venv && .venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
# Optional NLP model
python -m spacy download en_core_web_sm
```

### Environment
Create a `.env` file (values optional depending on your setup):
```env
MONGO_URI=mongodb://localhost:27017
USE_RL=true
RL_EXPLORATION_RATE=0.2
GROQ_API_KEY=your_key_if_used
GEMINI_API_KEY=your_key_if_used
QDRANT_URL=localhost:6333
```

### Run Services (recommended ports)
```powershell
# Terminal 1: Simple API (agents, KB endpoints)
python simple_api.py --port 8001

# Terminal 2: MCP Bridge (task router, RL, registry)
python mcp_bridge.py  # serves on port 8002

# Terminal 3: Web Interface (auth: admin/secret, user/secret)
python integration/web_interface.py  # serves on port 8003
```

### Endpoints
- Web UI: `http://localhost:8003`
- MCP Bridge health: `http://localhost:8002/health`
- Simple API docs: `http://localhost:8001/docs`

## Usage

### CLI
```bash
# Text
python cli_runner.py summarize "Explain artificial intelligence" edumentor_agent --input-type text

# Single file (auto-detect type)
python cli_runner.py summarize "Analyze this file" edumentor_agent --file sample_documents/ayurveda_basics.txt

# Batch directory → save CSV
python cli_runner.py summarize "Process folder" edumentor_agent --batch ./sample_documents --output results.csv --output-format csv

# RL options
python cli_runner.py summarize "Learning test" edumentor_agent --use-rl --rl-stats --exploration-rate 0.3
```

### MCP Bridge API (port 8002)
```bash
# JSON task
curl -X POST http://localhost:8002/handle_task \
  -H "Content-Type: application/json" \
  -d '{"agent":"edumentor_agent","input":"Explain machine learning","input_type":"text"}'

# Multi-task
curl -X POST http://localhost:8002/handle_multi_task \
  -H "Content-Type: application/json" \
  -d '{"files":[{"path":"test.pdf","type":"pdf","data":"Analyze"}],"agent":"edumentor_agent","task_type":"summarize"}'
```

### Simple API (port 8001)
```bash
# Vedas
curl -X POST http://localhost:8001/ask-vedas -H "Content-Type: application/json" -d '{"query":"what is dharma"}'

# Educational
curl -X POST http://localhost:8001/edumentor -H "Content-Type: application/json" -d '{"query":"explain reinforcement learning"}'

# Wellness
curl -X POST http://localhost:8001/wellness -H "Content-Type: application/json" -d '{"query":"how to reduce stress"}'

# Knowledge Base (uses NAS → FAISS → file retriever fallback)
curl -X POST http://localhost:8001/query-kb -H "Content-Type: application/json" -d '{"query":"agent architecture"}'

# Health
curl http://localhost:8001/health
```

### Web Interface (port 8003)
- Login with Basic Auth (`admin/secret` or `user/secret`)
- Upload files at `/` → processed via MCP Bridge
- Dashboard at `/dashboard` → recent tasks, NLO stats
- Download NLOs: `/download_nlo/{task_id}?format=json`

### Demo Pipeline
```bash
python blackhole_demo.py  # edit defaults within to point to your input
```

## Configuration
- Agent endpoints and options: `config/settings.py` and `agent_configs.json`
- RL configuration: `config/settings.py` (`RL_CONFIG`)
- Timeouts: `config/settings.py` (`TIMEOUT_CONFIG`)
- Knowledge base utilities: `bhiv_knowledge_base.py`, `utils/file_based_retriever.py`

Notes
- Start Simple API on port 8001 to match `agent_configs.json` and `MODEL_CONFIG` endpoints.
- For audio/image/PDF processing, ensure system deps like `ffmpeg`/`libsndfile` are available.

## Testing
```bash
pytest -q
# Or run focused suites
pytest tests/test_web_interface_integration.py -q
```

## Troubleshooting
- Check health:
  - `http://localhost:8002/health` (MCP Bridge)
  - `http://localhost:8001/health` (Simple API)
- Ports in use on Windows:
  - `netstat -ano | findstr :8001`
  - `netstat -ano | findstr :8002`
  - `netstat -ano | findstr :8003`
- Increase timeouts via environment or `config/settings.py` if large files stall.
- If KB search fails, Simple API falls back to FAISS (if indices present under `vector_stores/`) and then to file-based retriever over `local_setup/storage/documents/`.

## What’s New in Third Installment
- Unified Simple API with knowledge-base endpoints and model providers
- Reinforcement Learning context/logging integration in MCP Bridge
- Enhanced CLI with batch processing and multiple output formats
- Web UI with authentication, uploads, and NLO download

—

For advanced usage and deployment, see:
- `docs/complete_usage_guide.md`
- `docs/deployment.md`
- `example/quick_setup_guide.md`
