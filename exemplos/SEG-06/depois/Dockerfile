FROM python:3.13-alpine
# O pip não roda em produção, e as bibliotecas que ele embute entram na varredura.
RUN python -m pip uninstall -y pip && adduser -D app
USER app
COPY app.py /app/app.py
CMD ["python", "/app/app.py"]
