# Responsable : FOGAING FRANCK-NOEL
FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependances systeme minimales pour Pillow / TensorFlow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'ensemble du code source (app/, model/, scraping/).
# Le .dockerignore exclut les caches et les fichiers inutiles.
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--browser.serverAddress=localhost"]
