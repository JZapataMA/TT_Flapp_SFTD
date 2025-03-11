FROM python:3.10-slim

WORKDIR /app

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codigo fuente
COPY . .

# Puerto
ENV PORT=5000

# Exponer el puerto
EXPOSE $PORT

# Inicio
CMD ["python", "app.py"]