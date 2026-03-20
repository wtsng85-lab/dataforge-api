FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

# Copy only installed packages and app code
COPY --from=builder /deps /usr/local/lib/python3.12/site-packages/
COPY app/ app/

# Non-root user for security
RUN useradd -r -s /bin/false appuser
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
