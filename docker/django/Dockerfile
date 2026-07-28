# Single-stage: psycopg[binary] ships a self-contained wheel (no libpq
# build step needed), and this demo has no other compiled deps
# (no Pillow/reportlab), so a builder/runtime split isn't buying much.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# curl: used by docker-compose healthchecks against the django service.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=appuser:appuser src/ src/
RUN mkdir -p /app/src/staticfiles && chown appuser:appuser /app/src/staticfiles

USER appuser
WORKDIR /app/src

# No CMD — django, celery-worker, celery-beat, and flower services all
# use this same image with different `command:` overrides in
# docker-compose.yml: one image, no dependency drift between the web
# process, the worker, the scheduler, and the monitoring UI.
