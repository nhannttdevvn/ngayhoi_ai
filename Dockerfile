FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
COPY web web
COPY data data
COPY scripts scripts
RUN useradd -m ngayhoi && mkdir -p /app/out && chown ngayhoi /app/out
USER ngayhoi
ENV OUT_DIR=/app/out DB_PATH=/app/out/ngayhoi.db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
