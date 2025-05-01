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

- Python 3.10+
- FastAPI
- SQLite
- Firebase Authentication
- NewsAPI
- Poetry (Dependency Management)
- Pytest (Testing)
- Flake8 (Linting)
- Bandit (Security)

## Project Structure

```
news-aggregator/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core functionality and configuration
│   ├── db/            # Database models and operations
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic and external services
│   └── utils/         # Utility functions
├── tests/             # Test files
├── .env.example       # Environment variables template
├── pyproject.toml     # Project dependencies
└── README.md          # Project documentation
```

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
- Type checking: `poetry run mypy .`
- Security check: `poetry run bandit -r app`

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT
