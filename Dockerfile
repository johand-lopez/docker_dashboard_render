# Imagen base ligera de Python
FROM python:3.10-slim

# Configuración para evitar problemas con logs
ENV PYTHONUNBUFFERED=1

# Crear directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivos de requisitos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los archivos del proyecto
COPY . .

# Exponer el puerto 8501 (el de Streamlit)
EXPOSE 8501

# Comando de inicio (Streamlit corre app.py)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
