# Python Microservice

A modern Python microservice built with FastAPI.

## Features

- FastAPI for high-performance API development
- Docker containerization
- Testing with pytest
- Environment configuration with dotenv

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional)

### Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the service:
   ```
   uvicorn app.main:app --reload
   ```
4. Access the API at http://localhost:8000
5. API documentation at http://localhost:8000/docs

### Using Docker

```
docker build -t python-microservice .
docker run -p 8000:8000 python-microservice
```

## Project Structure

```
.
├── app/                # Application code
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── models/         # Data models
│   └── main.py         # Application entry point
├── tests/              # Test suite
├── .github/            # GitHub Actions workflows
├── Dockerfile          # Docker configuration
└── requirements.txt    # Python dependencies
```
