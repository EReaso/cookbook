FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for psycopg2 and Node.js
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@10.18.1

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY package.json pnpm-lock.yaml ./
RUN pnpm install

COPY . .

# Build SCSS to CSS
RUN pnpm run build

RUN chmod +x /app/entrypoint.sh

EXPOSE 5000
CMD ["/app/entrypoint.sh"]
