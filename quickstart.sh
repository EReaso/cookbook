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

# Step 2: Create the password file for Docker secrets
echo ""
echo "Setting up Docker secrets file..."

# Create .secrets directory if it doesn't exist
mkdir -p .secrets
chmod 700 .secrets

# Create the password file
echo "$POSTGRES_PASSWORD" > .secrets/postgres_password
chmod 600 .secrets/postgres_password
echo "Created .secrets/postgres_password file with secure permissions"

# Step 3: Install Node.js dependencies and build SCSS if not in Docker
echo ""
echo "Checking for local Node.js setup..."
if command -v pnpm &> /dev/null; then
    echo "Building SCSS to CSS..."
    pnpm install
    pnpm run build
    echo "SCSS built successfully"
else
    echo "Info: pnpm not found locally. SCSS will be built during Docker build."
fi

# Step 4: Build and start Docker containers
echo ""
echo "Building and starting Docker containers..."
$COMPOSE_CMD up --build -d

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 5

echo ""
echo "Setup complete!"
echo ""
echo "Summary:"
echo "  - Environment file: .env with generated SECRET_KEY and POSTGRES_PASSWORD"
echo "  - Docker secret file: .secrets/postgres_password"
echo "  - SCSS assets: Built and ready"
echo "  - Database: Automatically upgraded on container startup"
echo "  - Services: Running in background"
echo ""
echo "The application is now running at http://localhost:5000"
echo ""
echo "Other useful commands:"
echo "  - View logs: $COMPOSE_CMD logs -f"
echo "  - Stop services: $COMPOSE_CMD down"
echo "  - Remove data: $COMPOSE_CMD down -v"
echo "  - Rebuild: $COMPOSE_CMD up --build"
echo ""
