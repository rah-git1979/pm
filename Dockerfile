FROM node:20-slim AS frontend-build

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ ./
RUN npm install && npm run build:static

FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt backend/pyproject.toml /app/
RUN pip install --no-cache-dir uv && \
    pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend
COPY --from=frontend-build /build/out/. /app/backend/static/

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
