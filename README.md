# Flapp - APP DE PRUEBA TÉCNICA

## Descripción

La prueba técnica es una aplicación que actúa como intermediaria entre aplicaciones cliente y servicios de envío como TraeloYa y Uder. Permite generar carritos de compra con productos aleatorios y obtener cotizaciones de envío para estos productos.

## Requisitos previos

- Docker y Docker Compose
- Credenciales para las APIs de TraeloYa y Uder (configuradas en `.env` adjuntado en el correo)

## Instalación y configuración

1. Clonar el repositorio:
```cmd
git clone https://github.com/tu-usuario/flapp.git
cd flapp
```
2. Configurar las variables de entorno en un archivo .env en la raíz del proyecto:

```.env
DUMMY_API=https://dummyjson.com
UDER_CREDENTIAL=tu_credencial_uder
TRAELOYA_CREDENTIAL=tu_credencial_traeloya
UDER_URL=https://recruitment.weflapp.com/tarifier/uder
TRAELOYA_URL=https://recruitment.weflapp.com/tarifier/traelo_ya
```

3. Iniciar la aplicación con Docker Compose:

```cmd
docker-compose up -d
```

4. Acceder a la aplicación web:
```href
http://localhost:3000
```

## Estructura del proyecto
```
TT_Flapp_SFTD/
├── backend/                # Servicio backend (Flask)
│   ├── app.py              # Aplicación principal
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Servicio frontend (Nginx)
│   ├── index.html          # Página de carrito
│   ├── checkout.html       # Página de checkout
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── cart.js         # Lógica del carrito
│       └── checkout.js     # Lógica de checkout
└── docker-compose.yml      # Configuración Docker
```

## Funcionalidades

### Panel de compra (`index.html`)

- Generación de carritos aleatorios con productos de DummyJSON
- Visualización de productos en el carrito
- Navegación al checkout

### Checkout (`checkout.html`)

- Visualización del resumen del pedido
- Formulario para datos de envío
- Obtención de cotizaciones de envío
- Finalización de la compra

## Flujo de trabajo e interacción

1. ### Generación del carrito (cart.js):
    - El usuario hace clic en "Generar carrito"
    - Se realiza una petición a DummyJSON para obtener productos aleatorios
    - Se almacena el carrito en localStorage

2. ### Checkout y cotización (checkout.js):

    - El usuario completa sus datos de envío
    - Al hacer clic en "Cotizar envío", se envía el carrito al backend (/api/cart)
    - El backend procesa los productos y obtiene cotizaciones de TraeloYa y Uder
    - Se muestra la mejor cotización al usuario
3. ### Finalización del pedido:

    - El usuario hace clic en "Realizar pedido"
    - Se simula la finalización de la compra


## Endpoints API

### /api/cart (POST)
- Descripción: Procesa el carrito y obtiene cotizaciones de envío

- Payload:
```js
{
  "products": [
    {
      "productId": 123,
      "quantity": 2,
      "price": 10,
      "discount": 5,
      "title": "Producto",
      "thumbnail": "https://..."
    }
  ],
  "customer_data": {
    "name": "Usuario",
    "phone": "56912345678",
    "address": "Dirección",
    "commune": "Comuna",
    "shipping_street": "Calle"
  }
}
```

- Respuesta exitosa:
```js
{
  "courier": "TraeloYa",
  "price": 5000
}
```

- Respuesta de error:
```js
{
  "error": "Mensaje de error"
}
```

## Flujo interno del backend
- Recibe datos del carrito desde el frontend
- Obtiene información completa de productos desde DummyJSON
- Valida stock y otros detalles de los productos
- Construye payloads para las APIs de envío
- Realiza consultas asíncronas a TraeloYa y Uder
- Selecciona y devuelve la mejor cotización


## Supuestos