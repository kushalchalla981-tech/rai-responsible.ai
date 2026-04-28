<div align="center">

# RAI - Responsible AI

**Enterprise-Grade AI Fairness & Bias Detection Platform**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Detect • Analyze • Mitigate AI Bias**

</div>

---

## Overview

RAI is a comprehensive platform for auditing AI systems for fairness and bias. Built for enterprise use, it provides automated fairness analysis across multiple domains with real-time insights.

### Key Features

- **Multi-Mode Auditing**: Direct, Proxy, and Limited analysis modes
- **Comprehensive Metrics**: Demographic Parity, Equal Opportunity, Proxy Risk
- **Domain-Specific Analysis**: Hiring, Lending, Healthcare, Education, Criminal Justice
- **Real-Time Processing**: Instant analysis with detailed results
- **Enterprise-Ready**: Production-grade architecture

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+

### Installation

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Access
- **Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

---

## Usage

### 1. Upload Dataset
Upload your dataset in CSV or Excel format

### 2. Configure Audit
- Select target attribute (outcome variable)
- Choose protected attributes (demographics)
- Select audit mode (Direct/Proxy/Limited)
- Choose domain (Hiring/Lending/Healthcare/Education/Criminal Justice)

### 3. Run Analysis
Execute audit and receive comprehensive results

### 4. Review Results
Analyze metrics, findings, and recommendations

---

## Audit Modes

### Direct Mode
Direct fairness analysis with known protected attributes

### Proxy Mode  
Detect indirect discrimination through correlated features

### Limited Mode
Analyze data quality and confidence with limited information

---

## Supported Domains

| Domain | Use Case |
|--------|----------|
| **Hiring** | Employment decisions |
| **Lending** | Financial services |
| **Healthcare** | Medical treatment |
| **Education** | Learning outcomes |
| **Criminal Justice** | Legal decisions |

---

## API Reference

### Health Check
```http
GET /health
```

### Upload Dataset
```http
POST /api/v1/audit/upload
Content-Type: multipart/form-data
```

### Run Audit
```http
POST /api/v1/audit/run
Content-Type: application/json

{
  "dataset_id": "string",
  "mode": "direct|proxy|limited",
  "domain": "hiring|lending|healthcare|education|criminal_justice",
  "target_attribute": "string",
  "protected_attributes": ["string"],
  "confidence_threshold": 0.9
}
```

### Get Audit Results
```http
GET /api/v1/audit/results/{audit_id}
```

### List Audits
```http
GET /api/v1/audit/list
```

Complete API documentation: `http://localhost:8000/docs`

---

## Architecture

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Features**: RESTful API, Type-safe, Async processing

### Frontend
- **Framework**: Next.js 16
- **Language**: TypeScript
- **Features**: SSR, Type-safe, Responsive design

---

## Data Type Support

### Target Attributes
- Binary (0/1): hired, approved, outcome
- Numeric: age, income, score
- Categorical: department, category
- Boolean: True/False

### Protected Attributes
- Categorical: gender, race, department
- Numeric: age, income, experience
- High-cardinality: Automatically optimized

---

## Performance

- **Minimum Dataset Size**: 100 rows
- **Processing Time**: < 5 seconds
- **Memory Usage**: Linear scaling
- **Concurrent Users**: Multiple simultaneous audits

---

## Security

- **Data Privacy**: All data processed in-memory
- **No Persistence**: Datasets not stored permanently
- **Input Validation**: All inputs validated
- **CORS Protection**: Secure cross-origin requests

---

## Deployment

### Development
```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev
```

### Production
```bash
# Backend
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm start
```

---

## License

MIT License - See LICENSE file for details

---

<div align="center">

**Built for responsible AI development**

[⬆ Back to Top](#rai---responsible-ai)

</div>