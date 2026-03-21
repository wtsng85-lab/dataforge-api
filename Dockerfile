FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
