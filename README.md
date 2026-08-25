# SMARTA: Storage Monitoring & Real-time Tracking Assurance

## Overview
SMARTA is an AI-driven IoT ecosystem designed to tackle post-harvest food loss in storage facilities. By shifting away from static expiry dates, SMARTA provides real-time microclimate monitoring and proactive spoilage alerts, allowing warehouse managers to make data-driven decisions and prevent rapid, contagious spoilage.

## Key Features
* **Veggie AI Scanner:** Utilizes YOLOv8 to dynamically estimate shelf-life based on real-time visual conditions of the produce.
* **IoT Sensor Network:** Continuous live monitoring of critical microclimate metrics, including Temperature, Humidity, and Methane gas levels.
* **Proactive Alerts:** Employs an Isolation Forest machine learning model to detect environmental anomalies and trigger alerts before spoilage occurs.
* **Interactive Dashboard:** A centralized, real-time visualization interface for tracking telemetry data and warehouse inventory.

## Architecture & Tech Stack
The system is built using a modern, microservices-based architecture focused on performance, scalability, and continuous integration.

* **Backend:** FastAPI (for high-throughput, asynchronous API request handling)
* **Frontend/UI:** Streamlit (for rapid dashboard prototyping and live data visualization)
* **Database:** Supabase / PostgreSQL (for secure, real-time data syncing)
* **AI & Machine Learning:** YOLOv8 (Computer Vision), Isolation Forest (Anomaly Detection)
* **DevOps & Infrastructure:** Docker, Docker Compose, GitHub Actions (CI/CD)

## Getting Started

### Prerequisites
Make sure you have the following installed on your local machine:
* Docker
* Docker Compose
* Git

### Installation & Execution

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/smarta.git](https://github.com/your-username/smarta.git)
   cd smarta
