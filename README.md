# Mini-RAG Project

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

A production-ready **Retrieval-Augmented Generation (RAG)** system built with FastAPI, featuring asynchronous document processing, vector-based semantic search, and scalable AI-powered question answering.

## 🚀 Features

- **📄 Multi-format Document Processing**: Support for PDF, TXT files with automatic text extraction
- **🧠 AI-Powered Embeddings**: Integration with Cohere for high-quality text embeddings
- **🔍 Semantic Search**: Vector similarity search using PostgreSQL pgvector or Qdrant
- **💬 Question Answering**: RAG-based responses using OpenAI-compatible models
- **⚡ Asynchronous Processing**: Celery-based task queue for scalable document processing
- **📊 Monitoring & Observability**: Prometheus metrics with Grafana dashboards
- **🐳 Containerized Deployment**: Complete Docker Compose setup
- **🔄 Real-time Task Monitoring**: Flower dashboard for Celery task management
- **🗄️ Robust Data Management**: PostgreSQL with migration support via Alembic

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Client    │────│    Nginx     │────│   FastAPI   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                   ┌─────────────────────────────────────┐
                   │                                     │
           ┌───────▼────────┐                   ┌───────▼────────┐
           │  PostgreSQL    │                   │    Celery      │
           │  + pgvector    │                   │   Workers      │
           └────────────────┘                   └────────────────┘
                                                        │
                                           ┌────────────┼────────────┐
                                           │            │            │
                                    ┌─────▼──┐  ┌─────▼──┐  ┌──────▼──┐
                                    │ Qdrant │  │ Redis  │  │RabbitMQ │
                                    └────────┘  └────────┘  └─────────┘
```

## 📋 Prerequisites

- **Python 3.12** or higher
- **Docker & Docker Compose**
- **Git**

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/OmarEssameldinMousa/Mini-Rag-Project.git
cd Mini-Rag-Project
```

### 2. Environment Setup

#### Option A: Local Development

1. **Create Virtual Environment**
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

2. **Install Dependencies**
```bash
cd src
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cd ../docker/env
cp .env.example.app .env.app
cp .env.example.postgres .env.postgres
cp .env.example.rabbitmq .env.rabbitmq
cp .env.example.redis .env.redis
cp .env.example.grafana .env.grafana
```

4. **Update API Keys in `.env.app`**
```bash
# Required: Add your API keys
OPENAI_API_KEY="your_openai_api_key_here"
COHERE_API_KEY="your_cohere_api_key_here"
```

#### Option B: Docker-Only Setup

```bash
cd docker/env
# Copy all environment files
for file in .env.example.*; do cp "$file" "${file//.example/}"; done
# Update API keys in .env.app
```

### 3. Database Setup

```bash
cd docker
docker compose up pgvector rabbitmq redis -d
```

**Run Migrations**
```bash
cd ../src/models/db_schemes/minirag
source ../../../../env/bin/activate  # If using local setup
alembic upgrade head
```

## 🚀 Running the Application

### Using Docker Compose (Recommended)

```bash
cd docker
docker compose up --build
```

**Services will be available at:**
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Nginx (Load Balancer)**: http://localhost:81
- **Flower (Celery Monitor)**: http://localhost:5555
- **Grafana Dashboard**: http://localhost:3000
- **Prometheus Metrics**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672

### Local Development

```bash
# Terminal 1: Start services
cd docker
docker compose up pgvector rabbitmq redis qdrant prometheus grafana -d

# Terminal 2: Start FastAPI
cd src
source ../env/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start Celery Worker
celery -A celery_app worker --queues=default,file_processing,data_indexing --loglevel=info

# Terminal 4: Start Flower (optional)
celery -A celery_app flower --conf=flowerconfig.py
```

## 📚 API Usage

### 1. Upload Documents

```bash
curl -X POST "http://localhost:8000/data/upload/1" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf"
```

### 2. Process Documents

```bash
curl -X POST "http://localhost:8000/data/process/1"
```

### 3. Index for Search

```bash
curl -X POST "http://localhost:8000/nlp/index/push/1"
```

### 4. Search Documents

```bash
curl -X POST "http://localhost:8000/nlp/index/search/1" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "top_k": 5}'
```

### 5. Ask Questions (RAG)

```bash
curl -X POST "http://localhost:8000/nlp/index/answer/1" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the main concepts in the document"}'
```

## 🧪 API Testing

### Postman Collection
Import the Postman collection from `src/assets/mini-rag-app.postman_collection.json`

### Interactive Documentation
Visit http://localhost:8000/docs for Swagger UI documentation

## 📊 Monitoring

### Grafana Dashboards
- **URL**: http://localhost:3000
- **Default Credentials**: admin/admin (configure in `.env.grafana`)
- **Pre-configured Dashboards**: System metrics, PostgreSQL metrics, application metrics

### Celery Task Monitoring
- **Flower Dashboard**: http://localhost:5555
- **Password**: Set in `CELERY_FLOWER_PASSWORD` environment variable

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Available Metrics**: Application performance, database health, system resources

## 🔧 Configuration

### Supported File Types
- **PDF**: `.pdf`
- **Text**: `.txt`
- **Maximum file size**: 10MB (configurable)

### Vector Databases
- **PostgreSQL + pgvector**: Default, integrated with main database
- **Qdrant**: Dedicated vector database, better for large-scale deployments

## 🛠️ Development

### Project Structure
```
Mini-Rag-Project/
├── src/                          # Application source code
│   ├── main.py                   # FastAPI application entry
│   ├── celery_app.py            # Celery configuration
│   ├── routes/                   # API endpoints
│   ├── models/                   # Data models and database schemas
│   ├── controllers/              # Business logic
│   ├── tasks/                    # Celery tasks
│   ├── stores/                   # LLM and Vector DB providers
│   └── helpers/                  # Utilities and configuration
├── docker/                       # Docker configuration
│   ├── docker-compose.yml       # Service orchestration
│   ├── minirag/Dockerfile       # Application container
│   └── env/                      # Environment files
└── README.md
```
