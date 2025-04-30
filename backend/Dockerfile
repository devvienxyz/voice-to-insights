# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Optional system packages (remove if not needed)
RUN apt-get update && apt-get install -y build-essential && apt-get clean

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

# Healthcheck: ping the /health endpoint every 30s
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:10000/health || exit 1

# Gunicorn + Uvicorn: use port 10000 (Render default for Docker)
# CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000", "--workers=4", "--timeout=30"]
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_conf.py"]
