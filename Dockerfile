FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    OBRAZKY_DIR=/app/obrazky

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rosady rosady
COPY web web
COPY zdroje zdroje
# zmensene obrazky karet pro web se pripravi uz pri sestaveni
RUN python -m rosady.obrazky /app/obrazky

VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "rosady.server:vytvor_aplikaci", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
