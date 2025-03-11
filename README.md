# Flapp - APP DE PRUEBA TÉCNICA

## Descripción

La prueba técnica es una aplicación que actúa como intermediaria entre aplicaciones cliente y servicios de envío como TraeloYa y Uder. Permite generar carritos de compra con productos aleatorios y obtener cotizaciones de envío para estos productos.

## Requisitos previos

- Docker y Docker Compose
- Credenciales para las APIs de TraeloYa y Uder (configuradas en `.env` adjuntado en el correo)

## Instalación y configuración

1. Clonar el repositorio:
```bash
git clone https://github.com/JZapataMA/TT_Flapp_SFTD
cd TT_Flapp_SFTD
```
2. Configurar las variables de entorno en un archivo .env en la raíz del proyecto:

```python
DUMMY_API="https://dummyjson.com"
UDER_CREDENTIAL="tu_credencial_uder"
TRAELOYA_CREDENTIAL="tu_credencial_traeloya"
UDER_URL="https://recruitment.weflapp.com/tarifier/uder"
TRAELOYA_URL="https://recruitment.weflapp.com/tarifier/traelo_ya"
```

3. Iniciar la aplicación con Docker Compose:

```yaml
docker-compose up -d
```

4. Acceder a la aplicación web:
```bash
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

### Descripción General

El archivo `app.py` es el núcleo del backend de Flapp, implementado con Flask. Su función principal es procesar carritos de compra, validar productos y obtener cotizaciones de envío de diferentes servicios (TraeloYa y Uder).

### Tecnologías Utilizadas

- **Flask**: Framework web para Python
- **aiohttp**: Cliente HTTP asíncrono
- **asyncio**: Biblioteca para programación asíncrona
- **python-dotenv**: Carga de variables de entorno

### Estructura del Backend

#### Configuración Inicial

```python
load_dotenv()

credentials = {"uder": os.getenv("UDER_CREDENTIAL"), 
               "traeloya": os.getenv("TRAELOYA_CREDENTIAL")}

DUMMY_API = os.getenv("DUMMY_API")
TRAELOYA_URL = os.getenv("TRAELOYA_URL")
UDER_URL = os.getenv("UDER_URL")

app = Flask(__name__)
CORS(app)
```

## Funciones Principales

1. `fetch_all_products()`

Obtiene todos los productos disponibles de DummyJSON utilizando paginación asíncrona.

- Entrada: Ninguna
- Salida: Lista de productos
- Comportamiento: Realiza peticiones iterativas hasta obtener todos los productos

2. `process_cart_details(products, all_products)`
Valida los productos del carrito contra los datos completos de productos.

- Entrada:
  - products: Lista de productos en el carrito
  - all_products: Catálogo completo de productos
- Salida: Lista de productos procesados con información adicional
- Validaciones:
  - Existencia del producto
  - Stock suficiente
  - Cálculo de volumen y stock real

3. `build_shipping_payload(customer_data, cart_details)`

Construye el payload para solicitar cotizaciones de envío.

- Entrada:
  - customer_data: Datos del cliente
  - cart_details: Detalles del carrito procesado
- Salida: Estructura de datos para enviar a los servicios de cotización

4. `get_quotes(shipping_payload)`
- Entrada: Payload de envío
- Salida: Lista de cotizaciones
- Comportamiento:
  - Crea payloads específicos para cada servicio
  - Realiza peticiones asíncronas a ambos servicios
  - Procesa las respuestas

## Endpoint API

### /api/cart (POST)

Procesa el carrito y obtiene la mejor cotización de envío.

- Método: POST
- Payload:
```py
{
  "products": [...],
  "customer_data": {...}
}
```

- Flujo de procesamiento:
  1.  Recibe datos del carrito
  2.  Obtiene catálogo completo de productos
  3.  Procesa y valida el carrito
  4.  Construye payload para cotización
  5.  Obtiene cotizaciones de servicios externos
  6.  Selecciona la mejor cotización (menor precio)

## Integración con Servicios Externos

### 1. DummyJSON
- Propósito: Obtener información detallada de productos
- Endpoint: {DUMMY_API}/products
- Método de integración: GET con paginación
- Datos obtenidos: ID, título, precio, stock, rating, dimensiones

### 2. TraeloYa

- Propósito: Obtener cotización de envío
- Endpoint: {TRAELOYA_URL}
- Método de integración: POST con payload específico
- Formato de payload:
```py
{
  "items": [...],
  "waypoints": [...]
}
```
- Autenticación: Header X-Api-Key
- Datos obtenidos: Precio total del envío

### 3. Uder

- Propósito: Obtener cotización de envío alternativa
- Endpoint: {UDER_URL}
- Método de integración: POST con payload específico
- Formato de payload:
```py
{
  "pickup_address": "...",
  "pickup_name": "...",
  "manifest_items": [...]
}
```

- Autenticación: Header X-Api-Key
- Datos obtenidos: Tarifa de envío

## Manejo de Errores
- Producto no encontrado: Devuelve error 400 con mensaje descriptivo
- Stock insuficiente: Devuelve error 400 con mensaje descriptivo
- No hay envíos disponibles: Devuelve error 400 cuando no se obtienen cotizaciones
- Errores generales: Captura excepciones y devuelve error 400 con el mensaje de error


## Supuestos

- Se asume que los precios de salida de los servicios externos están correctos.
- El focus presente se dio totalmente en la api creada.
- Se realizaron consultas a modelos de IA Generativa para pulir codigo, optimizar consultar paralelas y para la ayuda de redacción.
- Dado a un error en particular con la conexión a los servicios externos que con las credenciales y una ardua investigación, me vi incapacitado de resolver, por ende deshabilité la verificación SSL.
- La mayor parte de manejo de errores es utilizando error 400 con un mensaje extra para guía
- Imploro vuestro perdón ante semejante tragedia de `.css` :D

<footer>
<p style="float:left; width: 70%;">
Copyright © Juan Manuel Zapata, 2025

juanmazm9@gmail.com
</p>
</footer>