# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    RADAR_PROJECT_DIR=/app RADAR_DATA_DIR=/var/lib/radar
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -c constraints.txt -r requirements.txt
COPY pyproject.toml ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir --no-deps . \
    && groupadd --gid 10001 radar \
    && useradd --uid 10001 --gid 10001 --create-home radar \
    && mkdir -p /var/lib/radar \
    && chown radar:radar /var/lib/radar

FROM base AS test
RUN pip install --no-cache-dir -c constraints.txt 'pytest>=8'
COPY tests ./tests
USER radar
ENV RADAR_ENV=test RADAR_DATA_DIR=/tmp/radar-test
CMD ["pytest", "-q"]

FROM base AS production
ENV RADAR_ENV=production
USER radar
EXPOSE 8050
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8050/health', timeout=3)"
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-", "radar.web.app:server"]
