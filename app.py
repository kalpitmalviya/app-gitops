from flask import Flask, render_template_string, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Sample products with free images from Picsum
products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 99.99,
        "image": "https://picsum.photos/300/200?random=1",
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation",
        "rating": 4.5
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 199.99,
        "image": "https://picsum.photos/300/200?random=2",
        "category": "Electronics",
        "description": "Feature-rich smartwatch with health monitoring",
        "rating": 4.2
    },
    {
        "id": 3,
        "name": "Running Shoes",
        "price": 79.99,
        "image": "https://picsum.photos/300/200?random=3",
        "category": "Fashion",
        "description": "Comfortable running shoes for all terrains",
        "rating": 4.7
    },
    {
        "id": 4,
        "name": "Coffee Maker",
        "price": 49.99,
        "image": "https://picsum.photos/300/200?random=4",
        "category": "Home",
        "description": "Automatic coffee maker with timer",
        "rating": 4.3
    },
    {
        "id": 5,
        "name": "Backpack",
        "price": 39.99,
        "image": "https://picsum.photos/300/200?random=5",
        "category": "Fashion",
        "description": "Waterproof backpack with laptop compartment",
        "rating": 4.6
    },
    {
        "id": 6,
        "name": "Desk Lamp",
        "price": 29.99,
        "image": "https://picsum.photos/300/200?random=6",
        "category": "Home",
        "description": "LED desk lamp with adjustable brightness",
        "rating": 4.4
    }
]

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopEasily - Premium Online Store</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Custom Variables */
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --accent: #ec4899;
            --success: #10b981;
        }

        html { scroll-behavior: smooth; }

        /* Glass-morphism navbar */
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }

        .logo-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }

        .search-box {
            background: #f9fafb;
            border: 2px solid transparent;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 12px;
        }

        .search-box:focus {
            background: white;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }

        .cart-icon:hover { transform: scale(1.1); color: #667eea; }

        .cart-badge {
            position: absolute; top: -8px; right: -8px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white; border-radius: 50%; width: 22px; height: 22px;
            font-size: 11px; font-weight: 600; display: flex;
            align-items: center; justify-content: center;
            animation: pulse-badge 2s ease-in-out infinite;
        }

        @keyframes pulse-badge {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
        }

        .hero-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            position: relative; overflow: hidden;
        }

        .product-card {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 16px; overflow: hidden; background: white;
            border: 1px solid #f0f0f0; position: relative;
        }

        .product-card:hover {
            transform: translateY(-12px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        .product-card img { transition: transform 0.5s ease; }
        .product-card:hover img { transform: scale(1.1); }

        .category-btn { transition: all 0.3s ease; border-radius: 10px; font-weight: 600; padding: 10px 20px; }
        .category-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        .category-btn:not(.active) { background: #f9fafb; color: #6b7280; }

        .add-to-cart-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: all 0.3s ease; border-radius: 10px; font-weight: 600;
        }
        .add-to-cart-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5); }

        .cart-sidebar {
            background: white; box-shadow: -10px 0 50px rgba(0, 0, 0, 0.15);
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .checkout-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        /* Toast Notification */
        .toast-notification {
            position: fixed; top: 100px; right: 20px;
            background: white; border-left: 4px solid #10b981;
            padding: 15px 25px; border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transform: translateX(200%); transition: transform 0.3s ease;
            z-index: 100; display: flex; items-center;
        }
        .toast-notification.show { transform: translateX(0); }
        
        .hero-cta {
            background: white; color: #667eea; font-weight: 700;
            padding: 14px 32px; border-radius: 12px; transition: all 0.3s ease;
        }
        .hero-cta:hover { transform: translateY(-4px) scale(1.05); }

        .img-container { overflow: hidden; }
        
        .badge-new {
            position: absolute; top: 10px; right: 10px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white; padding: 4px 12px; border-radius: 20px;
            font-size: 12px; font-weight: 600; z-index: 10;
        }
        
        .price-badge {
            background: #ecfdf5; color: #059669; padding: 4px 8px;
            border-radius: 6px; font-weight: bold;
        }

        .scroll-top {
            position: fixed; bottom: 30px; right: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 50px; height: 50px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: white; opacity: 0; pointer-events: none; transition: all 0.3s ease;
            z-index: 40;
        }
        .scroll-top.show { opacity: 1; pointer-events: all; }
    </style>
</head>
<body class="bg-gray-50">
    <nav class="navbar sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-3 cursor-pointer" onclick="window.scrollTo(0,0)">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                        <i class="fas fa-shopping-bag text-white text-lg"></i>
                    </div>
                    <span class="text-2xl logo-text">ShopEasily</span>
                </div>
                
                <div class="flex-1 max-w-2xl mx-8 hidden md:block">
                    <div class="relative">
                        <input type="text" id="searchInput" placeholder="Search for products..." 
                               class="w-full px-5 py-3 search-box focus:outline-none">
                        <i class="fas fa-search absolute right-4 top-4 text-gray-400"></i>
                    </div>
                </div>

                <div class="relative">
                    <button onclick="toggleCart()" class="p-3 text-gray-700 hover:text-indigo-600 cart-icon relative">
                        <i class="fas fa-shopping-cart text-2xl"></i>
                        <span id="cartCount" class="cart-badge" style="display: none;">0</span>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <section class="hero-gradient text-white py-20 relative">
        <div class="max-w-7xl mx-auto px-4 text-center relative z-10">
            <h1 class="text-5xl md:text-7xl font-black mb-6">Welcome to ShopEasily</h1>
            <p class="text-xl md:text-2xl mb-10 opacity-90 font-light">Discover amazing products at unbeatable prices ✨</p>
            <button onclick="scrollToProducts()" class="hero-cta">
                <i class="fas fa-arrow-down mr-2"></i>Start Shopping
            </button>
        </div>
    </section>

    <section id="products" class="max-w-7xl mx-auto px-4 py-16">
        <div class="text-center mb-12">
            <h2 class="text-4xl md:text-5xl font-bold text-gray-800 mb-4">Featured Products</h2>
        </div>
        
        <div class="flex flex-wrap justify-center gap-3 mb-12">
            <button onclick="filterProducts('all')" class="category-btn active" data-category="all">All Products</button>
            <button onclick="filterProducts('Electronics')" class="category-btn" data-category="Electronics">Electronics</button>
            <button onclick="filterProducts('Fashion')" class="category-btn" data-category="Fashion">Fashion</button>
            <button onclick="filterProducts('Home')" class="category-btn" data-category="Home">Home</button>
        </div>

        <div id="productsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {% for product in products %}
            <div class="product-card" data-category="{{ product.category }}" data-name="{{ product.name|lower }}">
                {% if product.id in [1, 3] %}
                <span class="badge-new">NEW</span>
                {% endif %}
                <div class="img-container">
                    <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-52 object-cover">
                </div>
                <div class="p-5">
                    <div class="flex justify-between items-start mb-3">
                        <h3 class="text-xl font-bold text-gray-800 flex-1">{{ product.name }}</h3>
                        <span class="price-badge ml-2">${{ product.price }}</span>
                    </div>
                    <p class="text-gray-600 text-sm mb-4 leading-relaxed">{{ product.description }}</p>
                    <div class="flex justify-between items-center">
                        <div class="flex items-center text-yellow-400">
                            <i class="fas fa-star"></i>
                            <span class="text-gray-600 ml-1 text-sm">{{ product.rating }}</span>
                        </div>
                        <button onclick="addToCart({{ product.id }})" 
                                class="add-to-cart-btn text-white px-5 py-2.5 text-sm transform active:scale-95">
                            <i class="fas fa-cart-plus mr-2"></i>Add to Cart
                        </button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>

    <div id="cartSidebar" class="fixed top-0 right-0 h-full w-96 cart-sidebar transform translate-x-full z-50 flex flex-col">
        <div class="p-5 border-b border-gray-200 flex justify-between items-center bg-gray-50">
            <h3 class="text-xl font-bold text-gray-800">Your Cart</h3>
            <button onclick="toggleCart()" class="text-gray-500 hover:text-red-500 text-xl"><i class="fas fa-times"></i></button>
        </div>
        
        <div id="cartItems" class="p-5 flex-1 overflow-y-auto">
            </div>
        
        <div class="p-5 border-t border-gray-200 bg-white">
            <div class="flex justify-between items-center mb-5">
                <span class="font-bold text-gray-700 text-lg">Total:</span>
                <span id="cartTotal" class="font-bold text-2xl text-indigo-600">$0.00</span>
            </div>
            <button onclick="checkout()" class="w-full checkout-btn text-white py-3 rounded-xl font-bold hover:shadow-lg transform active:scale-95 transition-all">
                Proceed to Checkout
            </button>
        </div>
    </div>

    <div id="cartOverlay" class="fixed inset-0 bg-black bg-opacity-40 hidden z-40" onclick="toggleCart()"></div>
    
    <div id="scrollTop" class="scroll-top" onclick="window.scrollTo(0,0)">
        <i class="fas fa-arrow-up"></i>
    </div>

    <div id="notificationArea"></div>

    <script>
        let cart = [];
        
        document.addEventListener('DOMContentLoaded', loadCart);

        function loadCart() {
            fetch('/get_cart')
                .then(response => response.json())
                .then(data => {
                    cart = data;
                    updateCartUI();
                });
        }

        function addToCart(productId) {
            fetch('/add_to_cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({product_id: productId})
            })
            .then(response => response.json())
            .then(data => {
                cart = data.cart;
                updateCartUI();
                showNotification('Item added to cart successfully!', 'success');
                // Open cart automatically on add
                const sidebar = document.getElementById('cartSidebar');
                const overlay = document.getElementById('cartOverlay');
                sidebar.classList.remove('translate-x-full');
                overlay.classList.remove('hidden');
            });
        }

        function removeFromCart(productId) {
            fetch('/remove_from_cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({product_id: productId})
            })
            .then(response => response.json())
            .then(data => {
                cart = data.cart;
                updateCartUI();
            });
        }

        function updateQuantity(productId, newQuantity) {
            if (newQuantity < 1) {
                removeFromCart(productId);
                return;
            }
            fetch('/update_quantity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({product_id: productId, quantity: newQuantity})
            })
            .then(response => response.json())
            .then(data => {
                cart = data.cart;
                updateCartUI();
            });
        }

        function updateCartUI() {
            const cartCount = document.getElementById('cartCount');
            const cartItems = document.getElementById('cartItems');
            const cartTotal = document.getElementById('cartTotal');

            const newCount = cart.reduce((total, item) => total + item.quantity, 0);
            cartCount.textContent = newCount;
            cartCount.style.display = newCount > 0 ? 'flex' : 'none';

            if (cart.length === 0) {
                cartItems.innerHTML = `
                    <div class="text-center text-gray-500 py-12">
                        <i class="fas fa-shopping-cart text-4xl mb-3 text-gray-300"></i>
                        <p>Your cart is empty</p>
                    </div>`;
                cartTotal.textContent = "$0.00";
            } else {
                let total = 0;
                cartItems.innerHTML = cart.map(item => {
                    total += item.price * item.quantity;
                    return `
                        <div class="flex items-center mb-4 bg-gray-50 p-3 rounded-lg">
                            <img src="${item.image}" class="w-16 h-16 object-cover rounded-md">
                            <div class="flex-1 ml-3">
                                <h4 class="font-bold text-sm text-gray-800">${item.name}</h4>
                                <p class="text-indigo-600 font-bold text-sm">$${item.price}</p>
                                <div class="flex items-center mt-2">
                                    <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})" class="bg-white w-6 h-6 rounded border shadow-sm">-</button>
                                    <span class="mx-3 text-sm font-semibold">${item.quantity}</span>
                                    <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})" class="bg-white w-6 h-6 rounded border shadow-sm">+</button>
                                </div>
                            </div>
                            <button onclick="removeFromCart(${item.id})" class="text-gray-400 hover:text-red-500 ml-2">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }).join('');
                cartTotal.textContent = `$${total.toFixed(2)}`;
            }
        }

        function toggleCart() {
            const sidebar = document.getElementById('cartSidebar');
            const overlay = document.getElementById('cartOverlay');
            sidebar.classList.toggle('translate-x-full');
            overlay.classList.toggle('hidden');
        }

        function filterProducts(category) {
            const products = document.querySelectorAll('.product-card');
            const buttons = document.querySelectorAll('.category-btn');

            buttons.forEach(btn => {
                if (btn.dataset.category === category) btn.classList.add('active');
                else btn.classList.remove('active');
            });

            products.forEach(product => {
                if (category === 'all' || product.dataset.category === category) {
                    product.style.display = 'block';
                    // Re-apply animation
                    product.style.animation = 'fadeIn 0.5s ease';
                } else {
                    product.style.display = 'none';
                }
            });
        }

        // Search Functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const products = document.querySelectorAll('.product-card');
            
            products.forEach(product => {
                const name = product.dataset.name;
                if (name.includes(searchTerm)) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        });

        function scrollToProducts() {
            document.getElementById('products').scrollIntoView({behavior: 'smooth'});
        }

        function checkout() {
            if (cart.length === 0) {
                showNotification('Your cart is empty!', 'error');
                return;
            }
            showNotification('Processing payment... (Demo Only)', 'success');
            setTimeout(() => {
                alert('Thank you for your purchase! This is a demo.');
                // Clear cart logic here if needed
            }, 1000);
        }

        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = 'toast-notification show';
            notification.innerHTML = `
                <i class="fas ${type === 'success' ? 'fa-check-circle text-green-500' : 'fa-info-circle text-blue-500'} mr-3 text-xl"></i>
                <span class="font-semibold text-gray-800">${message}</span>
            `;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }

        // Show/Hide Scroll to top
        window.addEventListener('scroll', () => {
            const scrollTopBtn = document.getElementById('scrollTop');
            if (window.scrollY > 300) {
                scrollTopBtn.classList.add('show');
            } else {
                scrollTopBtn.classList.remove('show');
            }
        });
    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, products=products)

@app.route('/get_cart')
def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    return jsonify(session['cart'])

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    
    # Check if item exists in cart
    found = False
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            found = True
            break
            
    if not found:
        # Find product details from global products list
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': 1
            })
    
    session['cart'] = cart # Save updates to session
    return jsonify({'success': True, 'cart': cart})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.json.get('product_id')
    if 'cart' in session:
        cart = session['cart']
        # Filter out the item to remove
        session['cart'] = [item for item in cart if item['id'] != product_id]
    
    return jsonify({'success': True, 'cart': session.get('cart', [])})

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity')
    
    if 'cart' in session:
        cart = session['cart']
        for item in cart:
            if item['id'] == product_id:
                item['quantity'] = quantity
                break
        session['cart'] = cart
        
    return jsonify({'success': True, 'cart': session.get('cart', [])})

if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible from outside the container
    app.run(host='0.0.0.0', port=5000, debug=True)
