from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime, timedelta
import random
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

products = [
    {"id": 1, "name": "Wireless Headphones", "price": 99.99, "original_price": 149.99, "image": "https://picsum.photos/300/200?random=1", "category": "Electronics", "description": "High-quality wireless headphones", "rating": 4.5, "stock": 15, "flash_sale": True, "sale_end": (datetime.now() + timedelta(hours=2)).isoformat()},
    {"id": 2, "name": "Smart Watch", "price": 199.99, "original_price": 199.99, "image": "https://picsum.photos/300/200?random=2", "category": "Electronics", "description": "Feature-rich smartwatch", "rating": 4.2, "stock": 8, "flash_sale": False, "sale_end": None},
    {"id": 3, "name": "Running Shoes", "price": 59.99, "original_price": 79.99, "image": "https://picsum.photos/300/200?random=3", "category": "Fashion", "description": "Comfortable running shoes", "rating": 4.7, "stock": 23, "flash_sale": True, "sale_end": (datetime.now() + timedelta(hours=1, minutes=30)).isoformat()},
    {"id": 4, "name": "Coffee Maker", "price": 49.99, "original_price": 49.99, "image": "https://picsum.photos/300/200?random=4", "category": "Home", "description": "Automatic coffee maker", "rating": 4.3, "stock": 12, "flash_sale": False, "sale_end": None},
    {"id": 5, "name": "Backpack", "price": 39.99, "original_price": 39.99, "image": "https://picsum.photos/300/200?random=5", "category": "Fashion", "description": "Waterproof backpack", "rating": 4.6, "stock": 30, "flash_sale": False, "sale_end": None},
    {"id": 6, "name": "Desk Lamp", "price": 29.99, "original_price": 29.99, "image": "https://picsum.photos/300/200?random=6", "category": "Home", "description": "LED desk lamp", "rating": 4.4, "stock": 18, "flash_sale": False, "sale_end": None}
]

active_users = {"count": random.randint(50, 150)}
recent_activities = []

def simulate_activity():
    activity_types = ["just purchased {product}", "is viewing {product}", "added {product} to cart"]
    while True:
        time.sleep(random.randint(3, 8))
        product = random.choice(products)
        activity = random.choice(activity_types).format(product=product['name'])
        location = random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"])
        recent_activities.insert(0, {"text": f"Someone from {location} {activity}", "timestamp": datetime.now().isoformat()})
        if len(recent_activities) > 10:
            recent_activities.pop()
        active_users["count"] = max(30, min(300, active_users["count"] + random.randint(-5, 8)))
        if random.random() < 0.3:
            product_to_update = random.choice(products)
            if product_to_update["stock"] > 0:
                product_to_update["stock"] = max(0, product_to_update["stock"] - random.randint(1, 2))

activity_thread = threading.Thread(target=simulate_activity, daemon=True)
activity_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_products')
def get_products():
    return jsonify(products)

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
    found = False
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            found = True
            break
    if not found:
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            cart.append({'id': product['id'], 'name': product['name'], 'price': product['price'], 'image': product['image'], 'quantity': 1})
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.json.get('product_id')
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
    return jsonify({'success': True, 'cart': session.get('cart', [])})

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity')
    if 'cart' in session:
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] = quantity
                break
    return jsonify({'success': True, 'cart': session.get('cart', [])})

@app.route('/get_realtime_updates')
def get_realtime_updates():
    return jsonify({
        'active_users': active_users['count'],
        'activities': recent_activities,
        'products': [{'id': p['id'], 'stock': p['stock']} for p in products]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
