document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos DOM
    const checkoutItems = document.getElementById('checkoutItems');
    const orderSubtotal = document.getElementById('orderSubtotal');
    const shippingCost = document.getElementById('shippingCost');
    const orderTotal = document.getElementById('orderTotal');
    const getQuotesBtn = document.getElementById('getQuotesBtn');
    const placeOrderBtn = document.getElementById('placeOrderBtn');
    const quoteLoading = document.getElementById('quoteLoading');
    const shippingOptions = document.getElementById('shippingOptions');
    
    // Formulario de envío
    const nameInput = document.getElementById('name');
    const phoneInput = document.getElementById('phone');
    const addressInput = document.getElementById('address');
    const communeInput = document.getElementById('commune');
    
    let cart = null;
    let selectedShipping = null;
    let subtotal = 0;

    //const API_BASE_URL = 'http://localhost:5000'; // Para localhost
    const API_BASE_URL = ''; // Para Docker

    // Verificar si hay un carrito almacenado
    const savedCart = localStorage.getItem('flappCart');
    
    if (!savedCart) {
        alert('No hay un carrito activo. Regresando al panel de compra.');
        window.location.href = 'index.html';
    } else {
        cart = JSON.parse(savedCart);
        displayCheckoutItems();
        
        // Prellenar formulario con datos del cliente
        if (cart.customer_data) {
            nameInput.value = cart.customer_data.name;
            phoneInput.value = cart.customer_data.phone;
            addressInput.value = cart.customer_data.address;
            communeInput.value = cart.customer_data.commune;
        }
    }
    
    // Función para mostrar los items en el checkout
    function displayCheckoutItems() {
        checkoutItems.innerHTML = '';
        subtotal = 0;
        
        cart.products.forEach(item => {
            const discountedPrice = item.price * (1 - item.discount / 100);
            const itemSubtotal = discountedPrice * item.quantity;
            subtotal += itemSubtotal;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${item.thumbnail}" alt="${item.title}" class="cart-item-image">
                        <span>${item.title}</span>
                    </div>
                </td>
                <td>$${discountedPrice.toFixed(2)}</td>
                <td>${item.quantity}</td>
                <td>$${itemSubtotal.toFixed(2)}</td>
            `;
            
            checkoutItems.appendChild(row);
        });
        
        orderSubtotal.textContent = `$${subtotal.toFixed(2)}`;
        updateOrderTotal();
    }
    
    // Función para actualizar el total del pedido
    function updateOrderTotal() {
        const shipping = selectedShipping ? selectedShipping.price : 0;
        const total = subtotal + shipping;
        orderTotal.textContent = `$${total.toFixed(2)}`;
    }
    
    // Función para obtener cotizaciones de envío
    async function getShippingQuotes() {
        try {
            // Actualizar datos del cliente en el carrito
            cart.customer_data = {
                name: nameInput.value,
                phone: phoneInput.value,
                address: addressInput.value,
                commune: communeInput.value,
                shipping_street: addressInput.value
            };
            
            // Guardar carrito actualizado
            localStorage.setItem('flappCart', JSON.stringify(cart));
            
            quoteLoading.classList.remove('d-none');
            getQuotesBtn.disabled = true;
            shippingCost.textContent = 'Calculando...';

            console.log('Enviando datos al backend:', JSON.stringify(cart));

            // Cotizaciones del backend
            const response = await fetch(`${API_BASE_URL}/api/cart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(cart)
            });
            
            console.log('Respuesta recibida. Status:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error en la respuesta:', errorData);
                
                // Verificar si es un error 400 específico para "No hay envíos disponibles"
                if (response.status === 400) {
                    shippingCost.textContent = 'No disponible';
                    shippingOptions.innerHTML = `
                        <div class="alert alert-warning">
                            No hay envíos disponibles :(
                        </div>
                    `;
                    return; // Salimos de la función sin lanzar error
                }
                
                throw new Error(errorData.error || `Error en la respuesta: ${response.status}`);
            }
            
            const quote = await response.json();
            console.log('Cotización recibida:', quote);

            displayShippingQuote(quote);
            
        } catch (error) {
            console.error('Error al obtener cotizaciones:', error);
            shippingCost.textContent = 'Error al calcular';
            shippingOptions.innerHTML = `
                <div class="alert alert-danger">
                    Error: ${error.message}
                </div>
            `;
            alert(`Error: ${error.message}`);
        } finally {
            quoteLoading.classList.add('d-none');
            getQuotesBtn.disabled = false;
        }
    }
    
    function displayShippingQuote(quote) {
        shippingCost.textContent = `$${quote.price.toFixed(2)}`;
        shippingOptions.innerHTML = `
            <div class="alert alert-success">
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="shippingOption" id="option_${quote.courier}" checked>
                    <label class="form-check-label d-flex justify-content-between" for="option_${quote.courier}">
                        <span>${quote.courier}</span>
                        <span>$${quote.price.toFixed(2)}</span>
                    </label>
                </div>
            </div>
        `;
        
        // Almacenar
        selectedShipping = quote;
        placeOrderBtn.disabled = false;
        
        // Actualizar el total
        updateOrderTotal();
    }
    
    // Función para finalizar el pedido
    function placeOrder() {
        alert('¡Pedido realizado con éxito!');
        localStorage.removeItem('flappCart');
        // Redirigir a una página de confirmación o al inicio
        window.location.href = 'index.html';
    }
    
    // Event listeners
    getQuotesBtn.addEventListener('click', getShippingQuotes);
    placeOrderBtn.addEventListener('click', placeOrder);
});