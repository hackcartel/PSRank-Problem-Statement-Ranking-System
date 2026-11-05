FROM python:3.12-slim

WORKDIR /app

COPY analyzer/ /app/analyzer/

RUN pip install --no-cache-dir -r analyzer/requirements.txt \
    && adduser --disabled-password --gecos "" appuser

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=3)"]

CMD ["sh", "-c", "uvicorn analyzer.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
