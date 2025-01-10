# 🦙 LlamaLaw

**Legal Contract Analysis and Management for LlamaSearch.ai**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

LlamaLaw is a powerful toolkit for legal contract analysis, management, and automation. It provides AI-powered capabilities for contract review, clause extraction, risk assessment, and legal document generation.

## 🚀 Key Features

- **Contract Analysis**: Extract key information, clauses, and obligations from legal documents
- **Risk Assessment**: Identify potential legal risks and compliance issues
- **Legal Document Generation**: Create legal documents from templates with variable substitution
- **Clause Library**: Maintain a library of standard legal clauses
- **Contract Management**: Track, store, and manage contracts through their lifecycle
- **Semantic Search**: Find relevant legal precedents and similar contracts
- **API Integration**: Integrate with existing legal and business systems

## 🧠 AI Capabilities

| Feature | Description |
|---------|------------|
| **Contract Classification** | Categorize legal documents by type and jurisdiction |
| **Entity Recognition** | Extract parties, dates, monetary values, and key entities |
| **Clause Extraction** | Identify and extract standard and custom clauses |
| **Obligation Detection** | Find and track legal obligations and responsibilities |
| **Risk Identification** | Flag potential issues and non-standard terms |
| **Summarization** | Generate plain-language summaries of legal documents |

## 📊 Sample Use Cases

- **Contract Review**: Automate the initial review of contracts to identify standard clauses and variations
- **Due Diligence**: Quickly analyze large volumes of contracts during mergers and acquisitions
- **Compliance Checking**: Ensure contracts comply with regulations and internal policies
- **Contract Generation**: Create legal documents from templates with automated variable filling
- **Knowledge Management**: Build a searchable repository of contracts and legal knowledge

## 🏗️ Project Structure

```
llamalaw/
├── src/
│   ├── llamalaw/
│   │   ├── __init__.py
│   │   ├── api/             # FastAPI application
│   │   │   ├── routes/      # API endpoints
│   │   │   ├── schemas/     # Pydantic models
│   │   │   └── deps.py      # Dependencies
│   │   ├── analysis/        # Document analysis
│   │   │   ├── extractor.py # Information extraction
│   │   │   ├── classifier.py # Document classification
│   │   │   └── risks.py     # Risk identification
│   │   ├── templates/       # Document templates
│   │   ├── storage/         # Storage adapters
│   │   ├── models/          # ML model interfaces
│   │   └── utils/           # Utility functions
├── tests/                   # Test suite
├── examples/                # Example usage
├── docs/                    # Documentation
├── setup.py                 # Package setup
└── requirements.txt         # Dependencies
```

## 💻 Getting Started

### Installation

```bash
# Install from PyPI
pip install llamalaw

# Or install from source
git clone https://llamasearch.ai
cd llamalaw
pip install -e .
```

### Quick Start

```python
from llamalaw import ContractAnalyzer

# Create an analyzer instance
analyzer = ContractAnalyzer()

# Analyze a contract
results = analyzer.analyze("path/to/contract.pdf")

# Extract key information
parties = results.parties
effective_date = results.dates.effective
term_length = results.term.length
obligations = results.obligations

# Get risk assessment
risks = results.risks
print(f"Found {len(risks)} potential risks")
for risk in risks:
    print(f"- {risk.description} (Severity: {risk.severity})")

# Generate a summary
summary = results.generate_summary()
print(summary)
```

### API Server

```bash
# Start the API server
llamalaw server start

# Or run with custom settings
llamalaw server start --host 0.0.0.0 --port 8080 --workers 4
```

Once running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Command Line Interface

```bash
# Analyze a contract
llamalaw analyze contract.pdf

# Generate a document from a template
llamalaw generate --template nda.tpl --output nda.pdf --vars vars.json

# Manage the clause library
llamalaw clauses list
llamalaw clauses add new_clause.json
llamalaw clauses search "indemnification"

# Search contracts
llamalaw search "termination clause"
```

## 🔧 API Endpoints

### Contract Management

- `GET /contracts`: List contracts
- `POST /contracts`: Upload a new contract
- `GET /contracts/{id}`: Get contract details
- `PUT /contracts/{id}`: Update contract metadata
- `DELETE /contracts/{id}`: Delete a contract

### Analysis

- `POST /analyze`: Analyze a contract
- `POST /analyze/risks`: Perform risk assessment
- `POST /analyze/summary`: Generate a summary
- `POST /analyze/extract`: Extract specific information

### Document Generation

- `GET /templates`: List available templates
- `POST /generate`: Generate a document from a template
- `POST /verify`: Verify a document against requirements

### Clause Library

- `GET /clauses`: List clauses
- `POST /clauses`: Add a new clause
- `GET /clauses/{id}`: Get clause details
- `PUT /clauses/{id}`: Update a clause
- `DELETE /clauses/{id}`: Delete a clause
- `POST /clauses/search`: Search for clauses

## 📚 Integration Examples

### Integration with LlamaSearch

```python
from llamalaw import ContractAnalyzer
from llamasearch import Index

# Create a searchable contract index
index = Index()

# Process contracts and add to index
analyzer = ContractAnalyzer()
contracts = analyzer.batch_analyze("contracts/")

for contract in contracts:
    index.add_document({
        "id": contract.id,
        "title": contract.title,
        "content": contract.text,
        "parties": contract.parties,
        "effective_date": contract.dates.effective,
        "expiration_date": contract.dates.expiration,
        "clauses": [c.text for c in contract.clauses],
        "obligations": [o.text for o in contract.obligations],
        "risks": [r.description for r in contract.risks]
    })

# Search for contracts
results = index.search("confidentiality obligations")
```

### Integration with LlamaAPI

```python
from llamaapi import create_api
from llamalaw.api import create_law_api

# Create a LlamaLaw API
law_api = create_law_api()

# Integrate with LlamaAPI
api = create_api()
api.add_routes(law_api.routes)

# Start the API
api.run()
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=llamalaw
```

## 📄 License

MIT License

## 🤝 Related Projects

- **LlamaPDF**: Document processing and extraction
- **LlamaSearch**: Semantic search capabilities
- **LlamaAPI**: API management and integration 
# Updated in commit 1 - 2025-04-04 17:33:46

# Updated in commit 9 - 2025-04-04 17:33:47

# Updated in commit 17 - 2025-04-04 17:33:47

# Updated in commit 25 - 2025-04-04 17:33:48

# Updated in commit 1 - 2025-04-05 14:36:32

# Updated in commit 9 - 2025-04-05 14:36:32
