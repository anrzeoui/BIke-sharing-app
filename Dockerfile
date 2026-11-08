FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Keep dependency installation cached when only application code changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bike_sharing/ ./bike_sharing/
COPY wsgi.py ./

RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid app --no-create-home app && \
    mkdir -p /app/instance && chown -R app:app /app/instance

USER app
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/healthz', timeout=2)" || exit 1

CMD ["gunicorn", "--workers", "1", "--access-logfile", "-", "--error-logfile", "-", "--bind", "0.0.0.0:3000", "wsgi:app"]
