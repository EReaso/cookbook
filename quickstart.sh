#!/usr/bin/env bash

# Cookbook Quickstart Script
# This script sets up the development environment with Docker secrets

set -euo pipefail

echo "🍳 Cookbook Quickstart Setup"
echo "============================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: docker-compose is not installed. Please install Docker Compose and try again."
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
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate a secure SECRET_KEY
    echo "🔐 Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || python -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "")
    
    if [ -z "$SECRET_KEY" ]; then
        echo "❌ Error: Failed to generate SECRET_KEY. Please ensure Python 3 is installed."
        exit 1
    fi
    
    # Replace the SECRET_KEY placeholder in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|# SECRET_KEY=your-generated-key-here|SECRET_KEY=$SECRET_KEY|g" .env
    else
        # Linux
        sed -i "s|# SECRET_KEY=your-generated-key-here|SECRET_KEY=$SECRET_KEY|g" .env
    fi
    
    echo "✅ Created .env with generated SECRET_KEY"
else
    echo "ℹ️  .env file already exists, skipping creation"
fi

# Step 2: Get or generate Postgres password
echo ""
echo "🔑 Setting up Postgres password..."
POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d '=' -f2-)

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "⚠️  Warning: POSTGRES_PASSWORD not found in .env, using default"
    POSTGRES_PASSWORD="cookbook_dev_password"
fi

echo "   Using password: $POSTGRES_PASSWORD"

# Step 3: Check if running in Swarm mode
if docker info 2>/dev/null | grep -q "Swarm: active"; then
    echo ""
    echo "🐝 Docker Swarm detected - setting up Docker secret..."
    
    # Check if secret already exists
    if docker secret ls --format "{{.Name}}" | grep -q "^postgres_password$"; then
        echo "ℹ️  Docker secret 'postgres_password' already exists"
        read -p "   Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   Removing existing secret..."
            docker secret rm postgres_password || true
            echo "$POSTGRES_PASSWORD" | docker secret create postgres_password -
            echo "✅ Recreated Docker secret 'postgres_password'"
        fi
    else
        echo "$POSTGRES_PASSWORD" | docker secret create postgres_password -
        echo "✅ Created Docker secret 'postgres_password'"
    fi
else
    echo ""
    echo "ℹ️  Docker Swarm not active - will use environment variables from .env"
    echo "   To use Docker secrets, initialize swarm with: docker swarm init"
    echo "   Then run this script again."
fi

# Step 4: Build and start services
echo ""
echo "🚀 Starting services with $COMPOSE_CMD..."
$COMPOSE_CMD up --build -d

# Wait for database to be ready
echo ""
echo "⏳ Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until $COMPOSE_CMD exec -T db pg_isready -U cookbook > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Error: Database failed to become ready after $MAX_RETRIES attempts"
        echo "   Check logs with: $COMPOSE_CMD logs db"
        exit 1
    fi
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done
echo "✅ Database is ready"

# Step 5: Run database migrations
echo ""
echo "🗄️  Running database migrations..."
if ! $COMPOSE_CMD exec -T web flask db upgrade; then
    echo "❌ Error: Database migrations failed"
    echo "   Check logs with: $COMPOSE_CMD logs web"
    echo "   You may need to run migrations manually: $COMPOSE_CMD exec web flask db upgrade"
    exit 1
fi
echo "✅ Migrations completed successfully"

echo ""
echo "✨ Setup complete!"
echo ""
echo "📋 Summary:"
echo "   • Environment file: .env"
echo "   • Database: PostgreSQL (cookbook)"
echo "   • Web app: http://localhost:5000"
echo ""
echo "🎯 Next steps:"
echo "   • Visit http://localhost:5000 to see your app"
echo "   • View logs: $COMPOSE_CMD logs -f"
echo "   • Stop services: $COMPOSE_CMD down"
echo "   • Remove data: $COMPOSE_CMD down -v"
echo ""
