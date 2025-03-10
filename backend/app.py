from flask import Flask, request, jsonify
import requests
import math
import os
from dotenv import load_dotenv
load_dotenv()

credentials = {"uder": os.getenv("UDER_CREDENTIAL"), 
               "traeloya": os.getenv("TRAELOYA_CREDENTIAL")}

app = Flask(__name__)

DUMMY_API = "https://dummyjson.com"

@app.route('/api/cart', methods=['POST'])
def process_cart():
    data = request.get_json()
    products = data.get('products', [])
    customer_data = data.get('customer_data', {})

    # Obtener todos los productos desde dummyjson con paginación de 10 en 10
    all_products = []
    page = 1
    limit = 10
    while True:
        response = requests.get(f"{DUMMY_API}/products", params={"limit": limit, "skip": (page - 1) * limit})
        if response.status_code != 200:
            return jsonify({"error": "Error al obtener productos de dummyjson"}), 400
        json_data = response.json()
        fetched_products = json_data.get('products', [])
        all_products.extend(fetched_products)
        if len(fetched_products) < limit:
            break
        page += 1

    cart_details = []
    # Procesar cada producto del carrito
    for item in products:
        prod_id = int(item.get('productId'))
        requested_quantity = item.get('quantity', 0)
        price = item.get('price', 0)
        discount = item.get('discount', 0)

        # Buscar producto en all_products
        product_info = next((p for p in all_products if p['id'] == prod_id), None)
        if not product_info:
            return jsonify({"error": f"Producto con id {prod_id} no encontrado"}), 400
        
        stock = product_info.get('stock', 0)
        rating = product_info.get('rating', 1)

        stock_real = math.floor(stock / rating)
        cart_details.append({
            "id": prod_id,
            "name": product_info.get('title'),
            "unit_price": price,
            "discount": discount,
            "quantity": requested_quantity,
            "stock": stock,
            "rating": rating,
            "stock_real": stock_real
        })
        # Verificar stock suficiente
        if requested_quantity > stock_real:
            return jsonify({"error": f"Stock insuficiente para el producto {product_info.get('title')}"}), 400

    # Imprimir en consola los detalles del carrito
    print("Detalles del carrito:")
    for detail in cart_details:
        print(detail)

    # Datos de origen para la tarificación
    origin_data = {
        "name": "Tienda Flapp",
        "phone": "56912345678",
        "address": "Juan de Valiente 3630",
        "commune": "Vitacura"
    }

    # Preparar payload para la tarificación
    shipping_payload = {
        "customer_data": customer_data,
        "cart": cart_details,
        "origin": origin_data
    }

    try:
        # Llamar a los endpoints de tarificación con las credenciales
        traelo_headers = {"Authorization": f"Bearer {credentials['traeloya']}"}
        response_traelo = requests.post(
            "https://recruitment.weflapp.com/tarifier/traelo_ya", 
            json=shipping_payload,
            headers=traelo_headers
        )
        
        uder_headers = {"Authorization": f"Bearer {credentials['uder']}"}
        response_uder = requests.post(
            "https://recruitment.weflapp.com/tarifier/uder", 
            json=shipping_payload,
            headers=uder_headers
        )

        quotes = []
        if response_traelo.status_code == 200:
            quotes.append({"courier": "TraeloYa", "price": response_traelo.json().get("price")})
        if response_uder.status_code == 200:
            quotes.append({"courier": "Uder", "price": response_uder.json().get("price")})
        if not quotes:
            return jsonify({"error": "No hay envíos disponibles"}), 400

        # Seleccionar la tarifa con menor precio
        best_quote = min(quotes, key=lambda x: x["price"])
    except Exception as e:
        return jsonify({"error": f"Error al tarificar: {str(e)}"}), 400

    return jsonify(best_quote)

if __name__ == '__main__':
    app.run(debug=True)
