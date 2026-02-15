#!/usr/bin/env bash

# Cookbook Quickstart Script
# This script sets up the development environment with Docker secrets

set -euo pipefail

echo "Cookbook Quickstart Setup"
echo "========================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Determine which compose command to use
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Using compose command: $COMPOSE_CMD"
echo ""

# Step 1: Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Generate a secure SECRET_KEY
    echo "Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || python -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "")
    
    if [ -z "$SECRET_KEY" ]; then
        echo "Error: Failed to generate SECRET_KEY. Please ensure Python 3 is installed."
        exit 1
    fi
    
    # Generate a secure POSTGRES_PASSWORD
    echo "Generating secure POSTGRES_PASSWORD..."
    POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || python -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "")
    
    if [ -z "$POSTGRES_PASSWORD" ]; then
        echo "Error: Failed to generate POSTGRES_PASSWORD. Please ensure Python 3 is installed."
        exit 1
    fi
    
    # Replace the SECRET_KEY and POSTGRES_PASSWORD placeholders in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|# SECRET_KEY=your-generated-key-here|SECRET_KEY=$SECRET_KEY|g" .env
        sed -i '' "s|POSTGRES_PASSWORD=cookbook_dev_password|POSTGRES_PASSWORD=$POSTGRES_PASSWORD|g" .env
    else
        # Linux
        sed -i "s|# SECRET_KEY=your-generated-key-here|SECRET_KEY=$SECRET_KEY|g" .env
        sed -i "s|POSTGRES_PASSWORD=cookbook_dev_password|POSTGRES_PASSWORD=$POSTGRES_PASSWORD|g" .env
    fi
    
    echo "Created .env with generated SECRET_KEY and POSTGRES_PASSWORD"
else
    echo "Info: .env file already exists, skipping creation"
fi

# Read password from .env for Docker secret setup
# This works for both newly created .env and pre-existing .env files
POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d '=' -f2-)

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Error: POSTGRES_PASSWORD not found in .env"
    echo "Please ensure your .env file contains: POSTGRES_PASSWORD=your_password"
    exit 1
fi

# Step 2: Check if running in Swarm mode
if docker info 2>/dev/null | grep -q "Swarm: active"; then
    echo ""
    echo "Docker Swarm detected - setting up Docker secret..."
    
    # Check if secret already exists
    if docker secret ls --format "{{.Name}}" | grep -q "^postgres_password$"; then
        echo "Info: Docker secret 'postgres_password' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Removing existing secret..."
            docker secret rm postgres_password || true
            echo "$POSTGRES_PASSWORD" | docker secret create postgres_password -
            echo "Recreated Docker secret 'postgres_password'"
        fi
    else
        echo "$POSTGRES_PASSWORD" | docker secret create postgres_password -
        echo "Created Docker secret 'postgres_password'"
    fi
else
    echo ""
    echo "Info: Docker Swarm not active - will use environment variables from .env"
    echo "To use Docker secrets, initialize swarm with: docker swarm init"
    echo "Then run this script again."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Summary:"
echo "  - Environment file: .env with generated SECRET_KEY and POSTGRES_PASSWORD"
echo "  - Docker secret: postgres_password (if Swarm mode active)"
echo ""
echo "To start the application, run:"
echo ""
echo "  $COMPOSE_CMD up --build"
echo ""
echo "Then in another terminal, run migrations:"
echo "  $COMPOSE_CMD exec web flask db upgrade"
echo ""
echo "The app will be available at http://localhost:5000"
echo ""
echo "Other useful commands:"
echo "  - View logs: $COMPOSE_CMD logs -f"
echo "  - Stop services: $COMPOSE_CMD down"
echo "  - Remove data: $COMPOSE_CMD down -v"
echo ""
