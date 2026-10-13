FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN python -m pip install --no-cache-dir ".[api]" \
    && useradd --create-home --uid 10001 codec \
    && chown -R codec:codec /app

USER codec
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent http://127.0.0.1:8000/health || exit 1

CMD ["python", "cli.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
