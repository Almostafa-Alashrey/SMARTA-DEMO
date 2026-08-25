# SMARTA - Intelligent IoT Storage Monitoring System

SMARTA is an AI-powered, end-to-end IoT storage monitoring system engineered to reduce food waste. It leverages state-of-the-art Computer Vision and Machine Learning algorithms to track environmental telemetry, detect anomalies, and predict spoilage in real-time.

## System Architecture

The system is composed of fully containerized microservices interacting seamlessly:
- **IoT Simulator:** Generates mock telemetry data (Temperature, Gas levels, etc.) representing physical sensors.
- **Backend (FastAPI):** The core API gateway handling data ingestion, processing, and routing.
- **AI Engine:**
  - **YOLOv8:** Computer vision model for scanning and identifying vegetables/fruits.
  - **Isolation Forest:** Machine learning algorithm for anomaly detection to identify potential spoilage based on telemetry data.
- **Database (PostgreSQL / Supabase):** Relational database storing inventory logs and telemetry records.
- **Frontend (Streamlit):** An interactive, real-time dashboard for monitoring storage health and managing inventory.

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Python-Multipart
- **Frontend:** Streamlit, Pandas, Plotly
- **AI/ML:** Ultralytics (YOLOv8), Scikit-Learn (Isolation Forest), OpenCV, NumPy
- **Database:** PostgreSQL (Local via Docker) / Supabase (Cloud Production)
- **DevOps:** Docker, Docker Compose, GitHub Actions (CI/CD)

---

## Getting Started (Local Development)

### Prerequisites
Make sure you have [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose installed on your machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/Almostafa-Alashrey/SMARTA.git](https://github.com/Almostafa-Alashrey/SMARTA.git)
cd SMARTA