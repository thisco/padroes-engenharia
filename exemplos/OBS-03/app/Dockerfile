FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.1.0 opentelemetry-distro==0.49b2 \
    opentelemetry-exporter-otlp==1.28.2 \
 && opentelemetry-bootstrap -a install
COPY app.py .
CMD ["opentelemetry-instrument", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
