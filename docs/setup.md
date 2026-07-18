# OmniBrain Setup Guide

## Overview

OmniBrain is an Agentic Multi-Modal RAG Orchestrator built using:

- Streamlit (Frontend)
- FastAPI (Backend)
- LangGraph
- Qdrant
- Vision Language Models (VLM)

---

# Prerequisites

Before running the project, install:

- Python 3.12+
- Git
- Docker Desktop (optional)

---

# Clone Repository

```bash
git clone <repository-url>
cd OmniBrain
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Frontend

```bash
streamlit run frontend/streamlit_app.py
```

The frontend will be available at:

```
http://localhost:8501
```

---

# Run with Docker

Build the frontend image:

```bash
docker build -f docker/Dockerfile.frontend -t omnibrain-frontend .
```

Run the container:

```bash
docker run -p 8501:8501 omnibrain-frontend
```

Open:

```
http://localhost:8501
```

---

# Project Structure

```
OmniBrain/
│
├── frontend/
│   └── streamlit_app.py
│
├── backend/
│
├── docker/
│   └── Dockerfile.frontend
│
├── docs/
│
└── requirements.txt
```

---

# Notes

- The frontend is developed using Streamlit.
- Backend APIs are developed using FastAPI.
- Docker support for additional services will be added as the project progresses.
