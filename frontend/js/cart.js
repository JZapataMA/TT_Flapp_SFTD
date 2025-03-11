document.addEventListener('DOMContentLoaded', () => {
    const generateCartBtn = document.getElementById('generateCartBtn');
    const checkoutBtn = document.getElementById('checkoutBtn');
    const cartContainer = document.getElementById('cartContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    // Estado del carrito
    let cart = {
        products: [],
        customer_data: {
            name: "Usuario de Prueba",
            phone: "56912345678",
            address: "Av. Providencia 1234",
            commune: "Providencia",
            shipping_street: "Av. Providencia 1234"
        }
    };

    // Función para generar un carrito aleatorio
    async function generateRandomCart() {
        try {
            // Mostrar indicador de carga
            loadingIndicator.classList.remove('d-none');
            cartContainer.classList.add('d-none');
            generateCartBtn.disabled = true;
            checkoutBtn.disabled = true;
            
            // Obtener productos aleatorios de DummyJSON
            const response = await fetch('https://dummyjson.com/products?limit=100');
            const data = await response.json();
            
            // Seleccionar 2-5 productos aleatorios
            const numProducts = Math.floor(Math.random() * 4) + 2;
            const selectedProducts = [];
            const usedIndexes = new Set();
            
            for (let i = 0; i < numProducts; i++) {
                let randomIndex;
                do {
                    randomIndex = Math.floor(Math.random() * data.products.length);
                } while (usedIndexes.has(randomIndex));
                
                usedIndexes.add(randomIndex);
                const product = data.products[randomIndex];
                
                selectedProducts.push({
                    productId: product.id,
                    quantity: Math.floor(Math.random() * 3) + 1,
                    price: product.price,
                    discount: Math.floor(Math.random() * 10),
                    title: product.title,
                    thumbnail: product.thumbnail
                });
            }
            
            // Actualizar el estado del carrito
            cart.products = selectedProducts;
            localStorage.setItem('flappCart', JSON.stringify(cart));
            
            // Mostrar el carrito
            displayCart();
            
            // Ocultar indicador de carga
            loadingIndicator.classList.add('d-none');
            cartContainer.classList.remove('d-none');
            generateCartBtn.disabled = false;
            checkoutBtn.disabled = false;
            
        } catch (error) {
            console.error('Error al generar el carrito:', error);
            loadingIndicator.classList.add('d-none');
            generateCartBtn.disabled = false;
            alert('Error al generar el carrito. Por favor, intente nuevamente.');
        }
    }
    
    // Función para mostrar el carrito
    function displayCart() {
        cartItems.innerHTML = '';
        
        let total = 0;
        
        cart.products.forEach(item => {
            const discountedPrice = item.price * (1 - item.discount / 100);
            const subtotal = discountedPrice * item.quantity;
            total += subtotal;
            
            const row = document.createElement('tr');
            row.className = 'product-row';
            row.innerHTML = `
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${item.thumbnail}" alt="${item.title}" class="cart-item-image">
                        <span>${item.title}</span>
                    </div>
                </td>
                <td>$${discountedPrice.toFixed(2)}</td>
                <td>${item.quantity}</td>
                <td>$${subtotal.toFixed(2)}</td>
            `;
            
            cartItems.appendChild(row);
        });
        
        cartTotal.textContent = `$${total.toFixed(2)}`;
    }
    
    // Función para ir al checkout
    function goToCheckout() {
        window.location.href = 'checkout.html';
    }
    
    // Verificar si hay un carrito almacenado
    const savedCart = localStorage.getItem('flappCart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        displayCart();
        cartContainer.classList.remove('d-none');
        checkoutBtn.disabled = false;
    }
    
    // Event listeners
    generateCartBtn.addEventListener('click', generateRandomCart);
    checkoutBtn.addEventListener('click', goToCheckout);
});