FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Variable para definir el puerto
ENV PORT=5000

# Exponer el puerto
EXPOSE $PORT

# Comando para iniciar la aplicación
CMD ["python", "app.py"]