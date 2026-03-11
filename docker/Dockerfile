# Usa un'immagine Python leggera
FROM python:3.12-slim

# Evita file .pyc e abilita output non bufferizzato
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installa le dipendenze prima per sfruttare la cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice sorgente
COPY . .

# Avvia il bot
CMD ["python", "main.py"]

