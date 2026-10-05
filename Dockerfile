FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir .
ENV RADAR_ENV=production RADAR_DATA_DIR=/var/lib/radar
RUN useradd --create-home radar && mkdir -p /var/lib/radar && chown radar:radar /var/lib/radar
USER radar
EXPOSE 8050
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8050/health')"
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "radar.web.app:server"]
