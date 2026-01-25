# Cookbook Recipe Management Application

A Flask-based web application for managing recipes with ingredients, images, and unit conversions.

## Features

- Recipe management with ingredients and directions
- Image upload and storage
- Unit conversions for recipe ingredients
- Ingredient density tracking for weight calculations
- Pagination support for recipe listings

## Requirements

- Python 3.10+
- Node.js 20+ (for SCSS compilation)
- pnpm package manager

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/EReaso/cookbook.git
cd cookbook
```

### 2. Set up Python virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

For development (includes testing and linting tools):

```bash
pip install -r requirements-dev.txt
```

### 4. Install Node.js dependencies

```bash
pnpm install
```

### 5. Initialize the database

```bash
flask db upgrade
```

### 6. Build CSS assets

```bash
pnpm run build
```

## Running the Application

### Development Server

```bash
python wsgi.py
```

The application will be available at `http://localhost:5000`

### Production Server

Use gunicorn:

```bash
gunicorn wsgi:wsgi_app
```

## Testing

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in your browser.

### Run specific test file

```bash
pytest tests/test_models.py
```

## Development

### Code Quality Tools

Format code with black:

```bash
black app tests
```

Sort imports with isort:

```bash
isort app tests
```

Lint code with flake8:

```bash
flake8 app tests
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

Run hooks manually:

```bash
pre-commit run --all-files
```

## Project Structure

```
cookbook/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── storage.py           # File storage handler
│   ├── recipes/             # Recipe blueprint
│   ├── images/              # Image blueprint
│   ├── models/              # Database models
│   ├── schemas/             # Data schemas
│   ├── static/              # Static files (CSS, JS)
│   └── templates/           # HTML templates
├── migrations/              # Database migrations
├── tests/                   # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_routes.py      # Route tests
│   ├── test_images.py      # Image route tests
│   └── test_storage.py     # Storage tests
├── .github/
│   └── workflows/          # CI/CD workflows
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── wsgi.py                 # WSGI entry point
```

## Database Migrations

Create a new migration:

```bash
flask db migrate -m "Description of changes"
```

Apply migrations:

```bash
flask db upgrade
```

Rollback migration:

```bash
flask db downgrade
```

## CI/CD

This project uses GitHub Actions for continuous integration:

- **Tests**: Runs on Python 3.10, 3.11, and 3.12
- **Linting**: Checks code quality with flake8, black, and isort
- **Coverage**: Uploads coverage reports to Codecov

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is open source and available under the MIT License.
