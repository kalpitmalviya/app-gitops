from flask import Flask, render_template_string, request, jsonify, session
import json
import os
from datetime import datetime, timedelta
import random
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Enhanced products with inventory and flash sale data
products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 99.99,
        "original_price": 149.99,
        "image": "https://picsum.photos/300/200?random=1",
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation",
        "rating": 4.5,
        "stock": 15,
        "flash_sale": True,
        "sale_end": (datetime.now() + timedelta(hours=2)).isoformat()
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 199.99,
        "original_price": 199.99,
        "image": "https://picsum.photos/300/200?random=2",
        "category": "Electronics",
        "description": "Feature-rich smartwatch with health monitoring",
        "rating": 4.2,
        "stock": 8,
        "flash_sale": False,
        "sale_end": None
    },
    {
        "id": 3,
        "name": "Running Shoes",
        "price": 59.99,
        "original_price": 79.99,
        "image": "https://picsum.photos/300/200?random=3",
        "category": "Fashion",
        "description": "Comfortable running shoes for all terrains",
        "rating": 4.7,
        "stock": 23,
        "flash_sale": True,
        "sale_end": (datetime.now() + timedelta(hours=1, minutes=30)).isoformat()
    },
    {
        "id": 4,
        "name": "Coffee Maker",
        "price": 49.99,
        "original_price": 49.99,
        "image": "https://picsum.photos/300/200?random=4",
        "category": "Home",
        "description": "Automatic coffee maker with timer",
        "rating": 4.3,
        "stock": 12,
        "flash_sale": False,
        "sale_end": None
    },
    {
        "id": 5,
        "name": "Backpack",
        "price": 39.99,
        "original_price": 39.99,
        "image": "https://picsum.photos/300/200?random=5",
        "category": "Fashion",
        "description": "Waterproof backpack with laptop compartment",
        "rating": 4.6,
        "stock": 30,
        "flash_sale": False,
        "sale_end": None
    },
    {
        "id": 6,
        "name": "Desk Lamp",
        "price": 29.99,
        "original_price": 29.99,
        "image": "https://picsum.photos/300/200?random=6",
        "category": "Home",
        "description": "LED desk lamp with adjustable brightness",
        "rating": 4.4,
        "stock": 18,
        "flash_sale": False,
        "sale_end": None
    }
]

# Track active users and recent activities
active_users = {"count": random.randint(50, 150)}
recent_activities = []

# Simulate real-time activities
def simulate_activity():
    """Background thread to simulate user activities"""
    activity_types = [
        "just purchased {product}",
        "is viewing {product}",
        "added {product} to cart"
    ]
    
    while True:
        time.sleep(random.randint(3, 8))
        
        # Random activity
        product = random.choice(products)
        activity = random.choice(activity_types).format(product=product['name'])
        location = random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"])
        
        recent_activities.insert(0, {
            "text": f"Someone from {location} {activity}",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 activities
        if len(recent_activities) > 10:
            recent_activities.pop()
        
        # Randomly adjust active users
        active_users["count"] = max(30, min(300, active_users["count"] + random.randint(-5, 8)))
        
        # Randomly decrease stock
        if random.random() < 0.3:
            product_to_update = random.choice(products)
            if product_to_update["stock"] > 0:
                product_to_update["stock"] = max(0, product_to_update["stock"] - random.randint(1, 2))

# Start background thread
activity_thread = threading.Thread(target=simulate_activity, daemon=True)
activity_thread.start()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopEasily - Live Shopping Experience</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --accent: #ec4899;
            --success: #10b981;
        }

        html { scroll-behavior: smooth; }

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
        .add-to-cart-btn:disabled {
            background: #d1d5db;
            cursor: not-allowed;
            transform: none;
        }

        .cart-sidebar {
            background: white; box-shadow: -10px 0 50px rgba(0, 0, 0, 0.15);
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .checkout-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .toast-notification {
            position: fixed; top: 100px; right: 20px;
            background: white; border-left: 4px solid #10b981;
            padding: 15px 25px; border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transform: translateX(200%); transition: transform 0.3s ease;
            z-index: 100; display: flex; align-items: center;
        }
        .toast-notification.show { transform: translateX(0); }
        
        .hero-cta {
            background: white; color: #667eea; font-weight: 700;
            padding: 14px 32px; border-radius: 12px; transition: all 0.3s ease;
        }
        .hero-cta:hover { transform: translateY(-4px) scale(1.05); }

        .img-container { overflow: hidden; position: relative; }
        
        .badge-new {
            position: absolute; top: 10px; right: 10px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white; padding: 4px 12px; border-radius: 20px;
            font-size: 12px; font-weight: 600; z-index: 10;
        }

        .badge-flash {
            position: absolute; top: 10px; left: 10px;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white; padding: 6px 12px; border-radius: 20px;
            font-size: 11px; font-weight: 700; z-index: 10;
            animation: flash-pulse 1.5s ease-in-out infinite;
        }

        @keyframes flash-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); box-shadow: 0 0 20px rgba(255, 107, 107, 0.6); }
        }
        
        .price-badge {
            background: #ecfdf5; color: #059669; padding: 4px 8px;
            border-radius: 6px; font-weight: bold;
        }

        .original-price {
            text-decoration: line-through;
            color: #9ca3af;
            font-size: 0.875rem;
        }

        .stock-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .stock-low {
            background: #fef3c7;
            color: #92400e;
            animation: stock-blink 2s ease-in-out infinite;
        }

        .stock-out {
            background: #fee2e2;
            color: #991b1b;
        }

        .stock-available {
            background: #d1fae5;
            color: #065f46;
        }

        @keyframes stock-blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .countdown-timer {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.875rem;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }

        .live-indicator {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            display: inline-block;
            animation: live-pulse 2s ease-in-out infinite;
            margin-right: 6px;
        }

        @keyframes live-pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        }

        .activity-feed {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 320px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            z-index: 45;
            max-height: 400px;
            overflow: hidden;
        }

        .activity-item {
            padding: 12px 16px;
            border-bottom: 1px solid #f3f4f6;
            font-size: 0.875rem;
            color: #4b5563;
            animation: slideInLeft 0.5s ease;
        }

        @keyframes slideInLeft {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        .stats-bar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 12px 20px;
            border-bottom: 1px solid #f3f4f6;
            display: flex;
            justify-content: space-around;
            align-items: center;
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
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

                <div class="flex items-center gap-4">
                    <div class="text-sm">
                        <span class="live-indicator"></span>
                        <span class="font-semibold text-gray-700"><span id="activeUsers">0</span> online</span>
                    </div>
                    <div class="relative">
                        <button onclick="toggleCart()" class="p-3 text-gray-700 hover:text-indigo-600 cart-icon relative">
                            <i class="fas fa-shopping-cart text-2xl"></i>
                            <span id="cartCount" class="cart-badge" style="display: none;">0</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <section class="hero-gradient text-white py-20 relative">
        <div class="max-w-7xl mx-auto px-4 text-center relative z-10">
            <h1 class="text-5xl md:text-7xl font-black mb-6">Welcome to ShopEasily</h1>
            <p class="text-xl md:text-2xl mb-4 opacity-90 font-light">Discover amazing products at unbeatable prices ✨</p>
            <p class="text-lg mb-10 opacity-80"><i class="fas fa-bolt mr-2"></i>Flash sales ending soon!</p>
            <button onclick="scrollToProducts()" class="hero-cta">
                <i class="fas fa-arrow-down mr-2"></i>Start Shopping
            </button>
        </div>
    </section>

    <section id="products" class="max-w-7xl mx-auto px-4 py-16">
        <div class="text-center mb-12">
            <h2 class="text-4xl md:text-5xl font-bold text-gray-800 mb-4">Featured Products</h2>
            <p class="text-gray-600">Live inventory updates • Real-time pricing</p>
        </div>
        
        <div class="flex flex-wrap justify-center gap-3 mb-12">
            <button onclick="filterProducts('all')" class="category-btn active" data-category="all">All Products</button>
            <button onclick="filterProducts('Electronics')" class="category-btn" data-category="Electronics">Electronics</button>
            <button onclick="filterProducts('Fashion')" class="category-btn" data-category="Fashion">Fashion</button>
            <button onclick="filterProducts('Home')" class="category-btn" data-category="Home">Home</button>
        </div>

        <div id="productsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        </div>
    </section>

    <div id="cartSidebar" class="fixed top-0 right-0 h-full w-96 cart-sidebar transform translate-x-full z-50 flex flex-col">
        <div class="p-5 border-b border-gray-200 flex justify-between items-center bg-gray-50">
            <h3 class="text-xl font-bold text-gray-800">Your Cart</h3>
            <button onclick="toggleCart()" class="text-gray-500 hover:text-red-500 text-xl"><i class="fas fa-times"></i></button>
        </div>
        
        <div id="cartItems" class="p-5 flex-1 overflow-y-auto"></div>
        
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

    <div class="activity-feed">
        <div class="stats-bar">
            <div class="stat-item">
                <i class="fas fa-fire text-orange-500"></i>
                <span class="font-semibold text-gray-700">Live Activity</span>
            </div>
        </div>
        <div id="activityFeed" class="overflow-y-auto" style="max-height: 320px;">
        </div>
    </div>

    <div id="cartOverlay" class="fixed inset-0 bg-black bg-opacity-40 hidden z-40" onclick="toggleCart()"></div>
    
    <div id="scrollTop" class="scroll-top" onclick="window.scrollTo(0,0)">
        <i class="fas fa-arrow-up"></i>
    </div>

    <script>
        let cart = [];
        let products = [];
        let countdownTimers = {};

        document.addEventListener('DOMContentLoaded', function() {
            loadCart();
            loadProducts();
            startRealtimeUpdates();
        });

        function loadCart() {
            fetch('/get_cart')
                .then(response => response.json())
                .then(data => {
                    cart = data;
                    updateCartUI();
                });
        }

        function loadProducts() {
            fetch('/get_products')
                .then(response => response.json())
                .then(data => {
                    products = data;
                    renderProducts();
                });
        }

        function renderProducts() {
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = products.map(product => {
                const stockClass = product.stock === 0 ? 'stock-out' : 
                                   product.stock <= 5 ? 'stock-low' : 'stock-available';
                const stockText = product.stock === 0 ? 'Out of Stock' :
                                  product.stock <= 5 ? `Only ${product.stock} left!` : 'In Stock';
                
                const isFlashSale = product.flash_sale;
                const priceDisplay = isFlashSale ? 
                    `<div class="flex items-center gap-2">
                        <span class="original-price">$${product.original_price}</span>
                        <span class="price-badge">$${product.price}</span>
                    </div>` : 
                    `<span class="price-badge">$${product.price}</span>`;

                return `
                    <div class="product-card" data-id="${product.id}" data-category="${product.category}" data-name="${product.name.toLowerCase()}">
                        ${isFlashSale ? '<span class="badge-flash"><i class="fas fa-bolt mr-1"></i>FLASH SALE</span>' : ''}
                        ${product.id === 1 || product.id === 3 ? '<span class="badge-new">NEW</span>' : ''}
                        <div class="img-container">
                            <img src="${product.image}" alt="${product.name}" class="w-full h-52 object-cover">
                        </div>
                        <div class="p-5">
                            <div class="flex justify-between items-start mb-3">
                                <h3 class="text-xl font-bold text-gray-800 flex-1">${product.name}</h3>
                                ${priceDisplay}
                            </div>
                            <p class="text-gray-600 text-sm mb-3 leading-relaxed">${product.description}</p>
                            
                            <div class="mb-3">
                                <span class="stock-badge ${stockClass}" data-product-id="${product.id}">
                                    ${stockText}
                                </span>
                            </div>

                            ${isFlashSale ? `<div class="countdown-timer" data-product-id="${product.id}" data-end-time="${product.sale_end}">
                                <i class="fas fa-clock"></i>
                                <span class="countdown-text">Loading...</span>
                            </div>` : ''}
                            
                            <div class="flex justify-between items-center mt-4">
                                <div class="flex items-center text-yellow-400">
                                    <i class="fas fa-star"></i>
                                    <span class="text-gray-600 ml-1 text-sm">${product.rating}</span>
                                </div>
                                <button onclick="addToCart(${product.id})" 
                                        ${product.stock === 0 ? 'disabled' : ''}
                                        class="add-to-cart-btn text-white px-5 py-2.5 text-sm transform active:scale-95">
                                    <i class="fas fa-cart-plus mr-2"></i>${product.stock === 0 ? 'Sold Out' : 'Add to Cart'}
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            products.forEach(product => {
                if (product.flash_sale && product.sale_end) {
                    startCountdown(product.id, product.sale_end);
                }
            });
        }

        function startCountdown(productId, endTime) {
            const timer = setInterval(() => {
                const now = new Date().getTime();
                const end = new Date(endTime).getTime();
                const distance = end - now;

                if (distance < 0) {
                    clearInterval(timer);
                    const element = document.querySelector(`[data-product-id="${productId}"].countdown-timer .countdown-text`);
                    if (element) element.textContent = 'Sale Ended';
                    return;
                }

                const hours = Math.floor(distance / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((distance % (1000 * 60)) / 1000);

                const element = document.querySelector(`[data-product-id="${productId}"].countdown-timer .countdown-text`);
                if (element) {
                    element.textContent = `${hours}h ${minutes}m ${seconds}s`;
                }
            }, 1000);

            countdownTimers[productId] = timer;
        }

        function startRealtimeUpdates() {
            setInterval(() => {
                fetch('/get_realtime_updates')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('activeUsers').textContent = data.active_users;
                        updateActivityFeed(data.activities);
                        updateProductStocks(data.products);
                    });
            }, 3000);
        }

        function updateActivityFeed(activities) {
            const feed = document.getElementById('activityFeed');
            feed.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <i class="fas fa-circle text-green-500 mr-2" style="font-size: 6px;"></i>
                    ${activity.text}
                </div>
            `).join('');
        }

        function updateProductStocks(updatedProducts) {
            updatedProducts.forEach(updated => {
                const product = products.find(p => p.id === updated.id);
                if (product && product.stock !== updated.stock) {
                    product.stock = updated.stock;
                    
                    const stockBadge = document.querySelector(`[data-product-id="${updated.id}"].stock-badge`);
                    if (stockBadge) {
                        const stockClass = updated.stock === 0 ? 'stock-out' : 
                                          updated.stock <= 5 ? 'stock-low' : 'stock-available';
                        const stockText = updated.stock === 0 ? 'Out of Stock' :
                                         updated.stock <= 5 ? `Only ${updated.stock} left!` : 'In Stock';
                        
                        stockBadge.className = `stock-badge ${stockClass}`;
                        stockBadge.textContent = stockText;
                        
                        if (updated.stock > 0 && updated.stock <= 3) {
                            showNotification(`⚠️ Only ${updated.stock} ${product.name} left!`, 'warning');
                        }
                    }

                    const button = document.querySelector(`[data-id="${updated.id}"] .add-to-cart-btn`);
                    if (button) {
                        if (updated.stock === 0) {
                            button.disabled = true;
                            button.innerHTML = '<i class="fas fa-cart-plus mr-2"></i>Sold Out';
                        } else {
                            button.disabled = false;
                            button.innerHTML = '<i class="fas fa-cart-plus mr-2"></i>Add to Cart';
                        }
                    }
                }
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
                const sidebar = document.getElementById('cartSi
