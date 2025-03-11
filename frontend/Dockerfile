FROM nginx:alpine

# Eliminar la configuración por defecto de nginx
RUN rm -rf /usr/share/nginx/html/*
RUN rm /etc/nginx/conf.d/default.conf

# Copiar los archivos estáticos del frontend
COPY . /usr/share/nginx/html

# Copiar la configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/

# Exponer el puerto 80 (despues se mappea al puerto 3000)
EXPOSE 80

# Inicio
CMD ["nginx", "-g", "daemon off;"]