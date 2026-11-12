# Autonomous Trade Finance & UCP 600 Letter of Credit Engine

A production-grade, distributed Trade Finance platform modeled after Tier-1 corporate and investment banking (CIB) architectures. It automates the examination of cross-border shipping documents under the **International Chamber of Commerce (ICC) UCP 600** and **ISBP 745** banking rules using **Spring Boot 3, Apache Kafka, Redis, PostgreSQL, MongoDB, Next.js 14, and LangGraph multi-agent AI**.

---

## 🏛 System Architecture & Tech Stack

```
[ Next.js 14 Web Workbench ] (Port 3000)
       |
  REST / WebSockets
       v
[ Spring Boot Core Banking ] (Port 8080)
  ├── Spring Security (JWT / RBAC Maker-Checker)
  ├── PostgreSQL (ACID Double-Entry Ledger & LC Registry)
  ├── MongoDB (Unstructured Shipping Documents & OCR Bounding Boxes)
  ├── Redis (Distributed Redlock, Idempotency, Session Store)
  └── Apache Kafka (Asynchronous Event Streaming Backbone)
       |
  Topic: 'trade.docs.uploaded'
       v
[ Python AI Agent Service (FastAPI + LangGraph) ] (Port 8000)
  ├── Day-1 PDF OCR Parser (pdfplumber + pytesseract)
  ├── UCP 600 Rule Evaluation Graph (Articles 14, 18, 20, 28)
  ├── Self-Correction OCR Re-examination Loop
  └── Automated SWIFT MT 734 Notice of Refusal Drafter
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
* **Java 17+**
* **Python 3.11 / 3.12**
* **Node.js 18+ / 20+**
* **Docker & Docker Compose**

### 1. Launch Distributed Infrastructure
```bash
cd docker
docker compose up -d
```
This spins up:
* **PostgreSQL 16** (`localhost:5432`) - Auto-migrates trade accounts and initial sample LC.
* **MongoDB 7.0** (`localhost:27017`) - Document store for trade packets.
* **Redis 7.0** (`localhost:6379`) - Distributed locks & cache.
* **Apache Kafka (KRaft mode)** (`localhost:9092`) - Event bus.
* **Zipkin** (`http://localhost:9411`) - Distributed tracing.
* **Prometheus** (`http://localhost:9090`) - Real-time metrics scraper.
* **Grafana** (`http://localhost:3001`) - Monitoring dashboards (User: `admin`, Pass: `admin`).

---

## 📂 Repository Structure

```
FinTech_Learn/
├── .github/workflows/ci.yml       # GitHub Actions CI/CD Pipeline
├── docker/
│   ├── docker-compose.yml         # Full infra stack (DBs, Kafka, Redis, Monitoring)
│   └── prometheus.yml             # Prometheus scraping definitions
├── services/
│   ├── core-banking-service/      # Spring Boot 3.2.5 microservice
│   │   ├── pom.xml                # Maven configuration
│   │   └── src/main/resources/
│   │       ├── application.yml    # App configuration & telemetry
│   │       └── db/migration/      # Flyway / PostgreSQL ACID schemas & seeds
│   └── ai-agent-service/          # Python 3.12 FastAPI + LangGraph microservice
│       └── requirements.txt       # AI, OCR, and Kafka dependencies
├── resources/
│   ├── swift-templates/           # Authentic SWIFT MT 700 & MT 734 specifications
│   └── test-documents/            # 10-case benchmark test suite (Pass & Discrepant PDFs)
└── README.md
```

---

## 📜 Key UCP 600 Rules Evaluated
* **Article 14 (Standard for Examination):** Cross-document consistency (e.g., Gross Weight on Packing List vs. Bill of Lading).
* **Article 18 (Commercial Invoice):** Exact goods description match against the LC clauses.
* **Article 20 (Bill of Lading):** Signed by carrier, dated "Shipped on Board", late shipment detection.
* **Article 28 (Insurance):** Minimum 110% coverage of CIF invoice value.
