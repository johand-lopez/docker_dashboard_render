# ======================================================
# Imagen base ligera
# ======================================================
FROM python:3.10-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# ======================================================
# Instalar dependencias del sistema necesarias para GeoPandas y GDAL
# ======================================================
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    python3-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# ======================================================
# Establecer directorio de trabajo
# ======================================================
WORKDIR /app

# ======================================================
# Copiar los archivos de dependencias e instalar
# ======================================================
COPY requirements.txt .
RUN python3 -m ensurepip
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# ======================================================
# Copiar el resto del proyecto
# ======================================================
COPY . .

# ======================================================
# Exponer el puerto (Render lo define dinámicamente)
# ======================================================
EXPOSE 8501

# ======================================================
# Comando para ejecutar Streamlit
# ======================================================
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
