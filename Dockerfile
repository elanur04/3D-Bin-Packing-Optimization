FROM python:3.10-slim

# Ortam değişkenleri ve çalışma dizini
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm kodları kopyala
COPY . .

# Cloud Run için varsayılan port 8080
EXPOSE 8080

# Streamlit uygulamasını başlat
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
