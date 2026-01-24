FROM python:3.11

WORKDIR /app

# Instala dependências de compilação
RUN apt-get update && apt-get install -y build-essential libpq-dev

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m appuser
USER appuser

COPY --chown=appuser:appuser ./shared /app/shared
COPY --chown=appuser:appuser ./backend /app/backend

EXPOSE 8000
