import math
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

credentials = {"uder": os.getenv("UDER_CREDENTIAL"), 
               "traeloya": os.getenv("TRAELOYA_CREDENTIAL")}

DUMMY_API = os.getenv("DUMMY_API")
TRAELOYA_URL = os.getenv("TRAELOYA_URL")
UDER_URL = os.getenv("UDER_URL")

app = Flask(__name__)
CORS(app)

async def fetch_all_products():
    """Retorna todos los productos desde dummyjson usando paginación async"""
    all_prodcuts = []
    page = 1
    limit = 10
    # Para testing, deshabilitamos la verificación SSL
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        while True:
            params = {"limit": limit, "skip": (page - 1) * limit}
            async with session.get(f"{DUMMY_API}/products", params=params) as response:
                if response.status != 200:
                    raise Exception("Error al obtener productos de dummyjson")
                json_data = await response.json()
                fetched_products = json_data.get('products', [])
                all_prodcuts.extend(fetched_products)
                if len(fetched_products) < limit:
                    break
                page += 1
    return all_prodcuts

def process_cart_details(products, all_products):
    """Procesa y valida los productos del carrito comparando con los productos de dummyjson"""	
    cart_details = []
    for item in products:
        prod_id = int(item.get('productId'))
        requested_quantity = item.get('quantity', 0)
        price = item.get('price', 0)
        discount = item.get('discount', 0)

        # Buscar producto en all_products
        product_info = next((p for p in all_products if p['id'] == prod_id), None)
        if not product_info:
            raise Exception(f"Producto con id {prod_id} no encontrado")
        
        stock = product_info.get('stock', 0)
        rating = product_info.get('rating', 1)
        stock_real = math.floor(stock / rating)
        dimensions = product_info.get('dimensions', {})
        volume = dimensions.get('height', 0) * dimensions.get('width', 0) * dimensions.get('depth', 0)

        cart_details.append({
            "id": prod_id,
            "name": product_info.get('title'),
            "unit_price": price,
            "discount": discount,
            "quantity": requested_quantity,
            "stock": stock,
            "rating": rating,
            "stock_real": stock_real,
            "dimensions": dimensions,
            "volume": volume
        })
        
        # Verificar stock suficiente
        if requested_quantity > stock_real:
            return jsonify({"error": f"No hay stock suficiente disponibles para {product_info.get('title')}"}), 400
    return cart_details

def build_shipping_payload(customer_data, cart_details):
    """Construye el payload para la tarificación"""
    origin_data = {
        "name": "Tienda Flapp",
        "phone": "56912345678",
        "address": "Juan de Valiente 3630",
        "commune": "Vitacura"
    }
    return {
        "customer_data": customer_data,
        "cart": cart_details,
        "origin": origin_data
    }

async def get_quotes(shipping_payload):
    """Obtiene las cotizaciones de envío de TraeloYa y Uder"""
    customer_data = shipping_payload.get('customer_data', {})
    cart_details = shipping_payload.get('cart', [])
    origin = shipping_payload.get('origin', {})

    traeloya_payload = {
        "items": [],
        "waypoints": [
            {
                "type": "PICK_UP",
                "addressStreet": origin.get("address"),
                "city": origin.get("commune"),
                "phone": origin.get("phone"),
                "name": origin.get("name")
            },
            {
                "type": "DROP_OFF",
                "addressStreet": customer_data.get("address"),
                "city": customer_data.get("commune"),
                "phone": customer_data.get("phone"),
                "name": customer_data.get("name")
            }
        ]
    }

    for product in cart_details:
        traeloya_payload["items"].append({
            "quantity": product.get("quantity", 0),
            "value": product.get("unit_price", 0),
            "volume": product.get("volume", 0)
        })

    uder_payload = {
        "pickup_address": origin.get("address"),
        "pickup_name": origin.get("name"),
        "pickup_phone_number": origin.get("phone"),
        "dropoff_address": customer_data.get("shipping_street"),
        "dropoff_name": customer_data.get("name"),
        "dropoff_phone_number": customer_data.get("phone"),
        "manifest_items": []
    }
    for product in cart_details:
        uder_payload["manifest_items"].append({
            "name": product.get("name"),
            "quantity": product.get("quantity", 0),
            "price": product.get("unit_price", 0),
            "dimensions": product.get("dimensions", 0)
        })

    # Para testing, deshabilitamos la verificación SSL en la sesión
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        traelo_headers = {"X-Api-Key": credentials['traeloya']}
        uder_headers = {"X-Api-Key": credentials['uder']}

        tasks = [
            session.post(TRAELOYA_URL, json=traeloya_payload, headers=traelo_headers),
            session.post(UDER_URL, json=uder_payload, headers=uder_headers)
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    ##########################################
    
        quotes = []
        # Procesamiento de respuestas

        # TraeloYa
        if not isinstance(responses[0], Exception) and responses[0].status == 200:
            traeloya_data = await responses[0].json()
            print("Respuesta de TraeloYa",traeloya_data, flush=True)
            delivery_offers = traeloya_data.get("deliveryOffers", {})
            pricing = delivery_offers.get("pricing", {})
            price = pricing.get("total")

            if price is not None:
                traeloya_quote = {
                    "courier": "TraeloYa",
                    "price": price
                }
                quotes.append(traeloya_quote)
        # Uder
        if not isinstance(responses[1], Exception) and responses[1].status == 200:
            resp_json = await responses[1].json()
            print("Respuesta de Uder", resp_json, flush=True)
            fee = resp_json.get("fee")
            if fee is not None:
                quotes.append({"courier": "Uder", "price": fee})
        return quotes

@app.route('/api/cart', methods=['POST'])
async def process_cart():
    try:
        data = request.get_json()
        products = data.get('products', [])
        customer_data = data.get('customer_data', {})

        # Recuperar productos de dummyjson de forma asíncrona
        all_products = await fetch_all_products()
        # Procesar y validar los productos del carrito
        cart_details = process_cart_details(products, all_products)
        display_keys = ["id", "name", "unit_price", "discount",
                        "quantity", "stock", "rating", "stock_real"]
        # desplegamos el carrito recibido solo con las llaves de display_keys
        cart_details_display = [{k: v for k, v in item.items() if k in display_keys} for item in cart_details]
        print("Carrito recibido:")
        for detail in cart_details_display:
            print(detail, flush=True)
        
        # Construir payload para tarificación
        shipping_payload = build_shipping_payload(customer_data, cart_details)
        # Obtener cotizaciones de forma asíncrona
        quotes = await get_quotes(shipping_payload)
        print("Cotizaciones:")
        print(quotes, flush=True)
        
        if not quotes:
            return jsonify({"error": "No hay envíos disponibles"}), 400
        
        # Seleccionar la tarifa con menor precio
        best_quote = min(quotes, key=lambda x: x["price"])
        return jsonify(best_quote)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
