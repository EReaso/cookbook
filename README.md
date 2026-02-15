# Cookbook Recipe Management Application

A Flask-based web application for managing recipes with ingredients, images, and unit conversions.

## Features

- Recipe management with ingredients and directions
- Image upload and storage
- Unit conversions for recipe ingredients
- Ingredient density tracking for weight calculations

## Requirements

- Python 3.10+
- Node.js 20+ (for SCSS compilation)
- pnpm package manager
- Docker & Docker Compose (optional, for containerized deployment)

## Environment Configuration

The application uses environment variables for configuration:

- `DATABASE_URL`: Database connection string (defaults to SQLite for local dev)
- `SECRET_KEY`: Flask secret key for session management and security

**Security Best Practices:**

1. **Never commit `.env` files** to version control (already in `.gitignore`)
2. **Generate strong SECRET_KEY** values:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. **For production**, use secure secret management:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets
   - GitHub Actions Secrets (for CI/CD)
4. **Rotate secrets regularly**

See `.env.example` for a template with detailed instructions.

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

### Option 1: Quick Start with Docker Compose (Recommended)

The easiest way to get started is with the quickstart script:

```bash
./quickstart.sh
```

This script will:
- Create a `.env` file with generated SECRET_KEY and POSTGRES_PASSWORD
- Set up Docker secrets for Postgres password (if Swarm mode is active)
- In non-Swarm mode, the password from `.env` will be used
- Provide you with the command to start the application

After running the script, start the application with the provided command:

```bash
docker-compose up --build
```

Then in another terminal, run database migrations:

```bash
docker-compose exec web flask db upgrade
```

The application will be available at `http://localhost:5000`

**Manual Setup (Alternative):**

If you prefer manual setup or the script doesn't work for your environment:

1. **Set up environment variables:**

```bash
cp .env.example .env
# Generate a secure SECRET_KEY and update .env
python -c "import secrets; print(secrets.token_hex(32))"
```

2. **Set up Docker secrets (optional, for Swarm mode):**

```bash
# Initialize Docker Swarm (if not already done)
docker swarm init

# Create the Postgres password secret
echo "your_secure_password" | docker secret create postgres_password -
```

For non-Swarm mode, the password from `.env` will be used automatically.

3. **Start the application:**

```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

4. **Run database migrations (in a new terminal):**

```bash
docker-compose exec web flask db upgrade
```

5. **Stop the application:**

```bash
docker-compose down
```

To remove volumes (including database data):

```bash
docker-compose down -v
```

**About Docker Secrets:**

This application supports Docker secrets for enhanced security. When running in Docker Swarm mode, the Postgres password is stored as a Docker secret instead of plain text in environment variables. The secret is marked as `external: true` to prevent accidentally committing secrets to the repository.

- **With Swarm mode:** Uses Docker secret `postgres_password`
- **Without Swarm mode:** Falls back to `POSTGRES_PASSWORD` from `.env`

See `.secrets/POSTGRES_PASSWORD.example` for the example secret format.

### Option 2: Local Development Server

For local development without Docker:

```bash
python wsgi.py
```

The application will be available at `http://localhost:5000`

### Option 3: Production Server

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

### Code Style

This project follows **Black's opinionated code style**:

- 4-space indentation
- Line length: 120 characters
- Double quotes for strings (with `skip-string-normalization` disabled by default)

**Linting and Formatting:**

- **Black**: Automatic code formatting
- **isort**: Import sorting (configured to work with Black)
- **flake8**: Style and quality linting

**Automated Formatting:**
The CI/CD pipeline automatically formats code with Black and isort on pull requests. If formatting changes are needed, they will be automatically committed to your PR branch by the GitHub Actions bot.

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

This project is open source and available under the GPL 3.0 License.
