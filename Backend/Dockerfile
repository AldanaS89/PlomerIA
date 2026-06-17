# Backend/Dockerfile — el build context es la RAÍZ del repo (ver docker-compose.yml),
# por eso las rutas son "requirements.txt" (raíz) y "Backend/" (código).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero para aprovechar la cache de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código del backend: queda en /app, junto a main.py (los imports son "from database import ...")
COPY Backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
