# Base image Python
FROM python:3.12-slim

# Imposta cartella lavoro
WORKDIR /app

# Copia tutti i file locali
COPY . /app
COPY static /app/static

# Aggiorna pip
RUN pip install --upgrade pip

# Installa tutte le librerie dal requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta di Streamlit
EXPOSE 8501

# Comando per avviare Streamlit
CMD ["streamlit", "run", "streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
