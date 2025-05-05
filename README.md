# AI-Powered News Aggregator

A modern news aggregator application that fetches and personalizes news content using AI-powered features.

## Features

- 🔐 User Authentication (Firebase Auth)
- 📰 News Fetching from Multiple Sources
- 🔍 Advanced Search Functionality
- 📑 Category-based Filtering
- 📌 Article Bookmarking
- 🚀 Fast and Responsive API

## Tech Stack

- Python 3.12+
- FastAPI
- SQLite
- Firebase Authentication
- NewsAPI
- Poetry (Dependency Management)
- Pytest (Testing)
- Flake8 (Linting)
- Bandit (Security)

## Setup

1. Clone the repository
2. Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
3. Install dependencies: `poetry install`
4. Copy `.env.example` to `.env` and fill in your credentials
5. Run the application: `poetry run uvicorn app.main:app --reload`

## Testing

Run tests with coverage:

```bash
PYTHONPATH=. poetry run pytest tests/
```

## Code Quality

- Linting: `poetry run flake8`
- Security check: `poetry run bandit -r app`

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT
