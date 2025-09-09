from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from models import GrabService, Actor, ACTOR_ISSUE_MAPPING, SERVICE_ACTORS, IssueCategory
import importlib

# Load environment variables from parent directory
load_dotenv(dotenv_path="../.env")

app = Flask(__name__)
CORS(app)

DATABASE_PATH = 'grabhack.db'

def safe_json_loads(json_string):
    """Safely parse JSON string, return empty dict if parsing fails"""
    if not json_string:
        return {}
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}, data: {json_string[:100]}...")
        return {}

def init_database():
    """Initialize the database with tables and sample data"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL,
            credibility_score INTEGER DEFAULT 7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Drop existing table and recreate with all required fields
    cursor.execute('DROP TABLE IF EXISTS orders')
    
    # Create orders table with all required fields
    cursor.execute('''
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            user_type TEXT NOT NULL,
            username TEXT NOT NULL,
            status TEXT NOT NULL,
            price REAL,
            start_location TEXT,
            end_location TEXT,
            customer_id TEXT,
            restaurant_id TEXT,
            driver_id TEXT,
            restaurant_name TEXT,
            food_items TEXT,
            cab_type TEXT,
            products_ordered TEXT,
            payment_method TEXT DEFAULT 'online',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    
    # Create complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            user_type TEXT NOT NULL,
            username TEXT NOT NULL,
            category TEXT NOT NULL,
            sub_issue TEXT NOT NULL,
            description TEXT NOT NULL,
            solution TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert comprehensive demo users with varied credibility scores
    demo_users = [
        # Customers with different credibility levels
        ('customer1', 'pass123', 'customer', 9),  # High credibility - loyal customer
        ('customer2', 'pass123', 'customer', 5),  # Medium credibility - some issues
        ('customer3', 'pass123', 'customer', 3),  # Low credibility - frequent complaints
        ('john_doe', 'pass123', 'customer', 8),   # Good customer
        ('jane_smith', 'pass123', 'customer', 7), # Average customer
        ('test_user', 'pass123', 'customer', 4),  # Test account - lower credibility
        
        # Delivery Agents
        ('agent1', 'pass123', 'delivery_agent', 8),
        ('agent2', 'pass123', 'delivery_agent', 7),
        ('agent3', 'pass123', 'delivery_agent', 9),
        ('fast_rider', 'pass123', 'delivery_agent', 8),
        
        # Restaurants
        ('resto1', 'pass123', 'restaurant', 7),
        ('resto2', 'pass123', 'restaurant', 6),
        ('resto3', 'pass123', 'restaurant', 8),
        ('pizza_palace', 'pass123', 'restaurant', 9),
        ('burger_joint', 'pass123', 'restaurant', 7),
        
        # Drivers (for cabs)
        ('driver1', 'pass123', 'driver', 8),
        ('driver2', 'pass123', 'driver', 7),
        ('driver3', 'pass123', 'driver', 6),
        
        # Dark stores
        ('store1', 'pass123', 'darkstore', 7),
        ('store2', 'pass123', 'darkstore', 8)
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO users (username, password, user_type, credibility_score) VALUES (?, ?, ?, ?)',
        demo_users
    )
    
    # Insert comprehensive demo orders for testing all scenarios
    demo_orders = [
        # === GRAB FOOD CUSTOMER ORDERS ===
        # High credibility customer (customer1) - mostly successful orders
        ('GF001', 'grab_food', 'customer', 'customer1', 'completed', 25.50, 
         'Pizza Palace Restaurant', '123 Oak Street Apartment 4B', 'CUST001', 'REST001', 'DRV001',
         'Pizza Palace', 'Margherita Pizza Large, Garlic Bread, Coca Cola', None, None,
         'online', '2024-08-15', '{"restaurant": "Pizza Palace", "total": 25.50, "rating": 5}'),
        
        ('GF002', 'grab_food', 'customer', 'customer1', 'completed', 32.75,
         'Burger Joint', '123 Oak Street Apartment 4B', 'CUST001', 'REST002', 'DRV002', 
         'Burger Joint', 'Double Cheeseburger, Large Fries, Chocolate Milkshake', None, None,
         'upi', '2024-08-20', '{"restaurant": "Burger Joint", "total": 32.75, "rating": 4}'),
        
        ('GF003', 'grab_food', 'customer', 'customer1', 'completed', 18.90,
         'Taco Bell', '123 Oak Street Apartment 4B', 'CUST001', 'REST003', 'DRV003',
         'Taco Bell', 'Crunchy Taco Supreme, Nachos, Pepsi', None, None,
         'card', '2024-09-01', '{"restaurant": "Taco Bell", "total": 18.90, "rating": 5}'),
        
        # Medium credibility customer (customer2) - mixed experience
        ('GF004', 'grab_food', 'customer', 'customer2', 'completed', 28.40,
         'Italian Bistro', '456 Pine Road House 12', 'CUST002', 'REST004', 'DRV004',
         'Italian Bistro', 'Chicken Alfredo, Caesar Salad, Garlic Bread', None, None,
         'cod', '2024-08-25', '{"restaurant": "Italian Bistro", "total": 28.40, "rating": 3}'),
         
        ('GF005', 'grab_food', 'customer', 'customer2', 'cancelled', 22.00,
         'Chinese Palace', '456 Pine Road House 12', 'CUST002', 'REST005', None,
         'Chinese Palace', 'Sweet and Sour Chicken, Fried Rice', None, None,
         'online', '2024-09-02', '{"restaurant": "Chinese Palace", "total": 22.00, "cancelled_reason": "long_wait"}'),
        
        ('GF006', 'grab_food', 'customer', 'customer2', 'in_progress', 19.75,
         'Subway', '456 Pine Road House 12', 'CUST002', 'REST006', 'DRV005',
         'Subway', 'Chicken Teriyaki Footlong, Cookies, Orange Juice', None, None,
         'online', '2024-09-06', '{"restaurant": "Subway", "total": 19.75}'),
        
        # Low credibility customer (customer3) - frequent complaints
        ('GF007', 'grab_food', 'customer', 'customer3', 'completed', 31.20,
         'Steakhouse', '789 Elm Avenue Floor 3', 'CUST003', 'REST007', 'DRV006',
         'Premium Steakhouse', 'Ribeye Steak, Mashed Potatoes, Wine', None, None,
         'card', '2024-08-30', '{"restaurant": "Premium Steakhouse", "total": 31.20, "rating": 2, "complaint": "food_cold"}'),
        
        ('GF008', 'grab_food', 'customer', 'customer3', 'cancelled', 15.50,
         'Fast Food Corner', '789 Elm Avenue Floor 3', 'CUST003', 'REST008', None,
         'Fast Food Corner', 'Chicken Nuggets, Fries', None, None,
         'cod', '2024-09-03', '{"restaurant": "Fast Food Corner", "total": 15.50, "cancelled_reason": "address_wrong"}'),
         
        # Good customer (john_doe)
        ('GF009', 'grab_food', 'customer', 'john_doe', 'completed', 45.80,
         'Sushi World', '321 Maple Drive Apartment 8A', 'CUST004', 'REST009', 'DRV007',
         'Sushi World', 'California Roll, Salmon Sashimi, Miso Soup, Green Tea', None, None,
         'online', '2024-09-05', '{"restaurant": "Sushi World", "total": 45.80, "rating": 5}'),
         
        # Average customer (jane_smith)
        ('GF010', 'grab_food', 'customer', 'jane_smith', 'completed', 27.30,
         'Mediterranean Grill', '654 Cedar Lane House 5', 'CUST005', 'REST010', 'DRV008',
         'Mediterranean Grill', 'Chicken Shawarma, Hummus, Pita Bread, Lemonade', None, None,
         'upi', '2024-09-04', '{"restaurant": "Mediterranean Grill", "total": 27.30, "rating": 4}'),
         
        # === GRAB EXPRESS CUSTOMER ORDERS ===
        # High credibility customer (customer1) - express delivery orders
        ('GE001', 'grab_express', 'customer', 'customer1', 'completed', 12.50,
         'Electronics Store Downtown', '123 Oak Street Apartment 4B', 'CUST001', None, 'EXP001',
         None, None, None, 'Smartphone Case, Screen Protector, Charging Cable',
         'online', '2024-09-01', '{"pickup_location": "Electronics Store Downtown", "delivery_time_minutes": 45, "vehicle_type": "Bike", "package_size": "Small", "rating": 5}'),
         
        ('GE002', 'grab_express', 'customer', 'customer1', 'completed', 25.80,
         'Office Supply Center', '123 Oak Street Apartment 4B', 'CUST001', None, 'EXP002', 
         None, None, None, 'Laptop Stand, Wireless Mouse, Notebook Set',
         'card', '2024-09-03', '{"pickup_location": "Office Supply Center", "delivery_time_minutes": 60, "vehicle_type": "Car", "package_size": "Medium", "rating": 4}'),
         
        ('GE003', 'grab_express', 'customer', 'customer1', 'in_progress', 35.00,
         'Furniture Warehouse', '123 Oak Street Apartment 4B', 'CUST001', None, 'EXP003',
         None, None, None, 'Office Chair (Disassembled), Desk Lamp',
         'cod', '2024-09-06', '{"pickup_location": "Furniture Warehouse", "estimated_delivery_minutes": 90, "vehicle_type": "Truck", "package_size": "Large", "special_instructions": "Fragile - Handle with care"}'),
        
        # === GRAB FOOD DELIVERY AGENT ORDERS ===
        ('GF011', 'grab_food', 'delivery_agent', 'agent1', 'assigned', 0.00,
         'Pizza Palace', '123 Oak Street Apartment 4B', None, 'REST001', 'agent1',
         'Pizza Palace', 'Pickup Order GF001', None, None,
         'online', '2024-09-06', '{"assigned_order": "GF001", "pickup_time": "19:30", "estimated_delivery": "20:00"}'),
         
        ('GF012', 'grab_food', 'delivery_agent', 'agent2', 'delivering', 0.00,
         'Burger Joint', '456 Pine Road House 12', None, 'REST002', 'agent2',
         'Burger Joint', 'Delivery in Progress Order GF006', None, None,
         'cod', '2024-09-06', '{"assigned_order": "GF006", "pickup_time": "20:15", "gps_issues": "true"}'),
         
        ('GF013', 'grab_food', 'delivery_agent', 'agent3', 'completed', 0.00,
         'Italian Bistro', '789 Elm Avenue Floor 3', None, 'REST004', 'agent3',
         'Italian Bistro', 'Completed Delivery GF007', None, None,
         'online', '2024-09-05', '{"assigned_order": "GF007", "delivery_time": "21:45", "customer_rating": 5}'),
         
        # === GRAB FOOD RESTAURANT ORDERS ===
        ('GF014', 'grab_food', 'restaurant', 'resto1', 'preparing', 0.00,
         'Restaurant Kitchen', 'Preparation Area', None, 'resto1', None,
         'Pizza Palace Kitchen', 'Preparing Order GF001 - Margherita Pizza', None, None,
         'online', '2024-09-06', '{"preparing_order": "GF001", "items": 3, "prep_time_minutes": 25}'),
         
        ('GF015', 'grab_food', 'restaurant', 'resto2', 'ready', 0.00,
         'Restaurant Kitchen', 'Pickup Counter', None, 'resto2', None,
         'Burger Joint Kitchen', 'Order Ready GF006 - Awaiting Pickup', None, None,
         'cod', '2024-09-06', '{"ready_order": "GF006", "items": 3, "waiting_time_minutes": 15, "ingredients_shortage": "pickles"}'),
         
        ('GF016', 'grab_food', 'restaurant', 'resto3', 'delayed', 0.00,
         'Restaurant Kitchen', 'Preparation Area', None, 'resto3', None,
         'Italian Bistro Kitchen', 'Delayed Order GF004 - High Volume', None, None,
         'online', '2024-09-06', '{"delayed_order": "GF004", "delay_reason": "high_volume", "estimated_delay_minutes": 30}'),
        
        # === GRAB CABS ORDERS ===
        # Customer cab orders
        ('GC001', 'grab_cabs', 'customer', 'customer1', 'completed', 15.00,
         'Downtown Mall', 'International Airport', 'CUST001', None, 'DRV101',
         None, None, 'Sedan', None,
         'upi', '2024-09-02', '{"from": "Downtown Mall", "to": "Airport", "distance_km": 12, "duration_minutes": 35}'),
         
        ('GC002', 'grab_cabs', 'customer', 'john_doe', 'in_progress', 8.50,
         'Central Railway Station', 'Business District Office Tower', 'CUST004', None, 'DRV102',
         None, None, 'Hatchback', None,
         'online', '2024-09-06', '{"from": "Railway Station", "to": "Business District", "driver_name": "Alex Kumar"}'),
         
        # Driver orders
        ('GC003', 'grab_cabs', 'driver', 'driver1', 'active', 12.75,
         'City Center', 'Residential Complex', 'CUST006', None, 'driver1',
         None, None, 'SUV', None,
         'cod', '2024-09-06', '{"passenger": "Sarah Wilson", "pickup": "City Center", "destination": "Green Valley"}'),
         
        ('GC004', 'grab_cabs', 'driver', 'driver2', 'completed', 22.30,
         'Hotel Grand Plaza', 'Shopping Mall', 'CUST007', None, 'driver2',
         None, None, 'Sedan', None,
         'card', '2024-09-05', '{"passenger": "Mike Johnson", "trip_rating": 5, "tip_amount": 2.50}'),
        
        # === GRAB MART ORDERS ===
        # Customer grocery orders
        ('GM001', 'grab_mart', 'customer', 'customer1', 'completed', 67.80,
         'FreshMart Store', '123 Oak Street Apartment 4B', 'CUST001', 'STORE001', 'DRV201',
         None, None, None, 'Milk, Bread, Eggs, Fruits, Vegetables, Cheese, Yogurt',
         'card', '2024-09-03', '{"store": "FreshMart", "items": 15, "total": 67.80, "delivery_instructions": "Leave at door"}'),
         
        ('GM002', 'grab_mart', 'customer', 'jane_smith', 'in_progress', 43.20,
         'SuperMart', '654 Cedar Lane House 5', 'CUST005', 'STORE002', 'DRV202',
         None, None, None, 'Rice, Cooking Oil, Spices, Onions, Potatoes, Chicken',
         'online', '2024-09-06', '{"store": "SuperMart", "items": 12, "special_instructions": "Call before delivery"}'),
         
        # Dark store orders
        ('GM003', 'grab_mart', 'darkstore', 'store1', 'picking', 58.90,
         'Dark Store Warehouse A', 'Customer Delivery Zone', 'CUST008', 'STORE001', None,
         None, None, None, 'Frozen Foods, Dairy Products, Snacks, Beverages',
         'cod', '2024-09-06', '{"picking_order": "GM002", "items_picked": 8, "items_remaining": 4, "picker_id": "PICK001"}'),
         
        ('GM004', 'grab_mart', 'darkstore', 'store2', 'completed', 91.45,
         'Dark Store Warehouse B', 'Premium Residential Area', 'CUST009', 'STORE002', 'DRV203',
         None, None, None, 'Organic Vegetables, Premium Meats, Imported Cheese, Wine',
         'card', '2024-09-04', '{"completed_order": "GM001", "items": 20, "quality_check": "passed", "delivery_rating": 4}'),
         
        # More grab_express orders for variety
        ('GE004', 'grab_express', 'customer', 'john_doe', 'completed', 18.90,
         'Medical Pharmacy', '321 Maple Drive Apartment 8A', 'CUST004', None, 'EXP004',
         None, None, None, 'Prescription Medicines, Medical Supplies',
         'online', '2024-09-02', '{"pickup_location": "Medical Pharmacy", "delivery_time_minutes": 30, "vehicle_type": "Bike", "package_size": "Small", "urgent_delivery": true, "rating": 5}'),
         
        ('GE005', 'grab_express', 'customer', 'jane_smith', 'completed', 42.60,
         'Home Appliance Store', '654 Cedar Lane House 5', 'CUST005', None, 'EXP005',
         None, None, None, 'Microwave Oven (Small), Kitchen Utensils Set',
         'upi', '2024-08-28', '{"pickup_location": "Home Appliance Store", "delivery_time_minutes": 75, "vehicle_type": "Car", "package_size": "Medium", "rating": 4}'),
         
        ('GE006', 'grab_express', 'customer', 'customer2', 'cancelled', 55.00,
         'Industrial Supply Co', '456 Pine Road House 12', 'CUST002', None, None,
         None, None, None, 'Heavy Machinery Parts, Tools Set',
         'cod', '2024-09-05', '{"pickup_location": "Industrial Supply Co", "cancelled_reason": "vehicle_capacity_insufficient", "required_vehicle": "Truck", "assigned_vehicle": "Car"}')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO orders 
        (id, service, user_type, username, status, price, start_location, end_location,
         customer_id, restaurant_id, driver_id, restaurant_name, food_items, cab_type, products_ordered, payment_method, date, details) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', demo_orders)
    
    # Insert demo complaints for credibility testing
    demo_complaints = [
        # High complaint frequency user (customer3) - affects credibility
        ('grab_food', 'customer', 'customer3', 'POOR_QUALITY', 'Food was cold and tasteless', 'Expired/damaged/poor quality items', 
         'We apologize for the quality issue. Full refund has been processed.', 'resolved', '2024-08-31 10:30:00'),
        
        ('grab_food', 'customer', 'customer3', 'ITEMS_MISSING', 'Missing garlic bread from my order', 'Missing items in delivery',
         'We have processed a partial refund for the missing item.', 'resolved', '2024-09-01 14:15:00'),
         
        ('grab_food', 'customer', 'customer3', 'FRAUD', 'Driver marked delivered but I never received the order', 'Driver marks delivered but no package received',
         'Investigation completed. Full refund issued and driver action taken.', 'resolved', '2024-09-04 18:45:00'),
         
        # Medium complaint user (customer2) - some issues
        ('grab_food', 'customer', 'customer2', 'ORDER_NOT_RECEIVED', 'Order was extremely late, over 1 hour delay', 'Delay beyond promised time',
         'We sincerely apologize for the delay. Compensation has been added to your account.', 'resolved', '2024-08-26 20:30:00'),
         
        ('grab_food', 'customer', 'customer2', 'PAYMENT_BILLING', 'Charged twice for the same order', 'Double charge for single order',
         'Double charge has been identified and refunded. Thank you for bringing this to our attention.', 'resolved', '2024-09-01 09:15:00'),
        
        # Occasional complaint from good user (customer1) - maintains credibility
        ('grab_food', 'customer', 'customer1', 'SPILLAGE', 'Food container was leaking', 'Cold/frozen items melted or leaked',
         'We apologize for the packaging issue. Replacement order has been arranged.', 'resolved', '2024-08-18 12:00:00'),
         
        # Test user complaints
        ('grab_food', 'customer', 'test_user', 'COUPON_QUERY', 'Discount coupon was not applied', 'Coupons/offers not applied correctly',
         'Coupon has been manually applied and refund processed.', 'resolved', '2024-09-05 16:30:00'),
         
        # Grab Express customer complaints
        ('grab_express', 'customer', 'customer1', 'PACKAGE_SIZE_VEHICLE_MISMATCH', 'My large package was assigned to a bike instead of truck', 'Package too large for bike delivery',
         'We apologize for the vehicle mismatch. Your package has been reassigned to a truck delivery partner and will arrive within 2 hours.', 'resolved', '2024-09-02 14:20:00'),
         
        ('grab_express', 'customer', 'customer2', 'VEHICLE_TYPE_REQUIREMENTS', 'Fragile electronics damaged during bike delivery', 'Fragile items need car instead of bike',
         'We sincerely apologize for the damage. A full refund has been processed and we have updated our system to ensure fragile items are assigned car delivery.', 'resolved', '2024-09-04 10:15:00'),
         
        # Delivery agent complaints
        ('grab_food', 'delivery_agent', 'agent2', 'GPS_APP_TECHNICAL_ISSUES', 'GPS not working, having trouble finding address', 'GPS and app technical support',
         'Technical support has been provided. GPS issue resolved.', 'resolved', '2024-09-06 19:00:00'),
         
        ('grab_food', 'delivery_agent', 'agent1', 'INCORRECT_CUSTOMER_ADDRESS', 'Customer provided wrong address, wasted 20 minutes', 'Incorrect customer address resolution',
         'Address has been corrected. Time compensation provided.', 'resolved', '2024-09-03 21:15:00'),
         
        # Restaurant complaints
        ('grab_food', 'restaurant', 'resto2', 'NOT_ENOUGH_DELIVERY_PARTNERS', 'No delivery agents available, orders getting delayed', 'Restaurant delivery partner shortage',
         'Additional delivery partners have been assigned to your area.', 'resolved', '2024-09-04 17:00:00'),
         
        ('grab_food', 'restaurant', 'resto3', 'LONG_WAITING_TIME', 'Too many orders, kitchen overwhelmed', 'Restaurant order preparation efficiency',
         'Order flow has been optimized. Kitchen support recommendations provided.', 'resolved', '2024-09-05 13:30:00')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO complaints 
        (service, user_type, username, category, description, sub_issue, solution, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', demo_complaints)
    
    conn.commit()
    conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login with auto user type detection"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Auto-detect user type by checking username and password
    cursor.execute(
        'SELECT id, username, user_type, credibility_score FROM users WHERE username = ? AND password = ?',
        (username, password)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_id, username, user_type, credibility_score = user
        
        # Define service mappings
        service_mappings = {
            'customer': ['grab_food', 'grab_cabs', 'grab_mart', 'grab_express'],
            'delivery_agent': ['grab_food', 'grab_mart'],
            'restaurant': ['grab_food'],
            'driver': ['grab_cabs'],
            'darkstore': ['grab_mart'],
            'express_delivery_partner': ['grab_express']
        }
        
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'user': {
                'id': user_id,
                'username': username,
                'user_type': user_type,
                'credibility_score': credibility_score,
                'services': service_mappings.get(user_type, [])
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/api/orders/<user_type>/<username>', methods=['GET'])
def get_orders(user_type, username):
    """Get orders for a specific user"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, service, user_type, username, status, price, start_location, end_location,
               customer_id, restaurant_id, driver_id, restaurant_name, food_items, cab_type, 
               products_ordered, payment_method, date, details 
        FROM orders 
        WHERE user_type = ? AND username = ? 
        ORDER BY date DESC
    ''', (user_type, username))
    
    orders = []
    for row in cursor.fetchall():
        orders.append({
            'id': row[0],
            'service': row[1],
            'user_type': row[2],
            'username': row[3],
            'status': row[4],
            'price': row[5],
            'start_location': row[6],
            'end_location': row[7],
            'customer_id': row[8],
            'restaurant_id': row[9],
            'driver_id': row[10],
            'restaurant_name': row[11],
            'food_items': row[12],
            'cab_type': row[13],
            'products_ordered': row[14],
            'payment_method': row[15],
            'date': row[16],
            'details': safe_json_loads(row[17])
        })
    
    conn.close()
    return jsonify({'orders': orders})

@app.route('/api/categories/<service>/<user_type>', methods=['GET'])
def get_categories(service, user_type):
    """Get handler files as main categories from the folder structure"""
    try:
        service_name = service
        user_type_folder = user_type if user_type != 'darkstore' else 'dark_house'
        
        # Map frontend user types to backend folder structure
        folder_mapping = {
            'customer': 'customer',
            'delivery_agent': 'delivery_agent', 
            'restaurant': 'restaurant',
            'driver': 'driver',
            'darkstore': 'dark_house'
        }
        
        folder_name = folder_mapping.get(user_type, user_type)
        
        # Get handler files from the appropriate service/user folder
        handler_path = f"{service_name}/{folder_name}"
        
        categories = []
        
        if service_name == 'grab_food' and folder_name == 'customer':
            categories = [
                {'id': 'order_quality_handler', 'name': 'Order Quality & Accuracy'},
                {'id': 'delivery_experience_handler', 'name': 'Delivery Experience'},
                {'id': 'driver_interaction_handler', 'name': 'Driver Interaction'},
                {'id': 'payment_refund_handler', 'name': 'Payment & Refunds'},
                {'id': 'technical_handler', 'name': 'Technical Issues'}
            ]
        elif service_name == 'grab_food' and folder_name == 'delivery_agent':
            categories = [
                {'id': 'technical_handler', 'name': 'Technical Support'},
                {'id': 'navigation_location_handler', 'name': 'Navigation & Location'},
                {'id': 'logistics_handler', 'name': 'Logistics Support'},
                {'id': 'operational_handler', 'name': 'Operational Issues'}
            ]
        elif service_name == 'grab_food' and folder_name == 'restaurant':
            categories = [
                {'id': 'restaurant_handler', 'name': 'Restaurant Operations'}
            ]
        elif service_name == 'grab_cabs' and folder_name == 'customer':
            categories = [
                {'id': 'ride_experience_handler', 'name': 'Ride Experience'}
            ]
        elif service_name == 'grab_cabs' and folder_name == 'driver':
            categories = [
                {'id': 'customer_experience', 'name': 'Customer Experience Issues'},
                {'id': 'driver_vehicle_issues', 'name': 'Driver & Vehicle Issues'},
                {'id': 'fare_payment', 'name': 'Fare & Payment Issues'},
                {'id': 'operational_issues', 'name': 'Operational Issues'},
                {'id': 'operational_problems', 'name': 'Operational Problems'}
            ]
        elif service_name == 'grab_mart' and folder_name == 'customer':
            categories = [
                {'id': 'shopping_experience_handler', 'name': 'Shopping Experience'}
            ]
        elif service_name == 'grab_mart' and folder_name == 'delivery_agent':
            categories = [
                {'id': 'grocery_delivery_handler', 'name': 'Grocery Delivery'}
            ]
        elif service_name == 'grab_mart' and folder_name == 'dark_house':
            categories = [
                {'id': 'inventory_handler', 'name': 'Inventory Management'}
            ]
        elif service_name == 'grab_express' and folder_name == 'customer':
            categories = [
                {'id': 'order_quality_handler', 'name': 'Package Quality & Accuracy'},
                {'id': 'delivery_experience_handler', 'name': 'Express Delivery Experience'},
                {'id': 'driver_interaction_handler', 'name': 'Delivery Partner Interaction'},
                {'id': 'payment_refund_handler', 'name': 'Payment & Refunds'},
                {'id': 'technical_handler', 'name': 'Technical Issues'},
                {'id': 'vehicle_matching_handler', 'name': 'Vehicle Type & Capacity'},
                {'id': 'express_service_handler', 'name': 'Express Service Features'},
                {'id': 'special_handling_handler', 'name': 'Special Package Handling'}
            ]
        
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/subissues/<service>/<user_type>/<category_id>', methods=['GET'])
def get_subissues(service, user_type, category_id):
    """Get sub-issues from the models.py mapping based on service, user type, and category"""
    try:
        service_enum = GrabService(service)
        actor_enum = Actor(user_type if user_type != 'darkstore' else 'dark_house')
        
        # Get the issues mapping for this service and actor
        issues_mapping = ACTOR_ISSUE_MAPPING.get((service_enum, actor_enum), {})
        
        # Special handling for grab_cabs driver with new handler structure
        if service == 'grab_cabs' and user_type == 'driver':
            sub_issues = []
            
            if category_id == 'customer_experience':
                sub_issues = [
                    {'id': 'handle_passenger_harassment_complaint', 'name': 'Passenger Harassment/Rude Behavior', 'description': 'Report inappropriate passenger behavior'},
                    {'id': 'handle_false_complaint_rating_reduction', 'name': 'False Complaint & Rating Issues', 'description': 'Address unfair complaints and rating reductions'},
                    {'id': 'handle_unresolved_passenger_disputes', 'name': 'Unresolved Passenger Disputes', 'description': 'Get help with ongoing passenger conflicts'}
                ]
            elif category_id == 'driver_vehicle_issues':
                sub_issues = [
                    {'id': 'handle_vehicle_breakdown_during_ride', 'name': 'Vehicle Breakdown During Ride', 'description': 'Emergency vehicle breakdown support'},
                    {'id': 'handle_passenger_damage_coverage', 'name': 'Passenger Damage Coverage', 'description': 'Report and claim passenger-caused vehicle damage'},
                    {'id': 'handle_insurance_fuel_maintenance_support', 'name': 'Insurance/Fuel/Maintenance Support', 'description': 'Get support for vehicle maintenance and insurance'}
                ]
            elif category_id == 'fare_payment':
                sub_issues = [
                    {'id': 'handle_incorrect_fare_calculation', 'name': 'Incorrect Fare Calculation', 'description': 'Report fare calculation errors'},
                    {'id': 'handle_payout_not_received', 'name': 'Payout Not Received', 'description': 'Issues with payment processing and delays'},
                    {'id': 'handle_high_commission_rates', 'name': 'High Commission Rates', 'description': 'Concerns about commission structure'}
                ]
            elif category_id == 'operational_issues':
                sub_issues = [
                    {'id': 'handle_passenger_cancellation_after_arrival', 'name': 'Passenger Cancellation After Arrival', 'description': 'Compensation for cancelled rides after reaching pickup'},
                    {'id': 'handle_wrong_pickup_drop_details', 'name': 'Wrong Pickup/Drop Details', 'description': 'Issues with incorrect ride details'},
                    {'id': 'handle_long_waiting_time_compensation', 'name': 'Long Waiting Time Compensation', 'description': 'Get compensation for excessive waiting times'}
                ]
            elif category_id == 'operational_problems':
                sub_issues = [
                    {'id': 'handle_no_rides_during_peak_hours', 'name': 'No Rides During Peak Hours', 'description': 'Low ride allocation during busy times'},
                    {'id': 'handle_unfair_ride_allocation', 'name': 'Unfair Ride Allocation', 'description': 'Issues with ride distribution and fairness'},
                    {'id': 'handle_incorrect_navigation_route', 'name': 'Incorrect Navigation/Route', 'description': 'GPS and navigation route problems'}
                ]
            
            return jsonify({'subissues': sub_issues})
        
        # Default handling for other services
        sub_issues = []
        
        for category, sub_issue_list in issues_mapping.items():
            # Check if any sub-issue's handler_module matches the category_id pattern
            for sub_issue in sub_issue_list:
                if category_id in sub_issue.handler_module:
                    sub_issues.append({
                        'id': sub_issue.tool_name,
                        'name': sub_issue.name,
                        'description': sub_issue.description
                    })
        
        return jsonify({'subissues': sub_issues})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/complaint', methods=['POST'])
def submit_complaint():
    """Submit a complaint and get AI response"""
    data = request.json
    
    # Store complaint in database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO complaints (service, user_type, username, category, sub_issue, description, solution, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['service'],
        data['user_type'],
        'anonymous',  # In real app, get from auth
        data['category'],
        data['sub_issue'],
        data['description'],
        '',  # Will be filled by AI
        'processing'
    ))
    
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Generate AI response using direct AI engine
    try:
        from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
        ai_engine = EnhancedAgenticAIEngine()
        
        solution = ai_engine.process_complaint(
            function_name=data['sub_issue'],
            user_query=data['description'],
            service=data['service'],
            user_type=data['user_type'],
            image_data=data.get('image_data'),
            username=data.get('username', 'anonymous')
        )
        
        print(f"AI Engine Success: {len(solution)} characters generated")
        
        # Fallback if AI fails
        if not solution or len(solution) < 100:
            solution = f"AI processing temporarily unavailable. Your complaint has been received and logged. Customer service will respond within 24 hours."
            
    except Exception as e:
        print(f"AI Engine Error: {e}")
        solution = f"AI processing error. Your complaint has been received and logged. Customer service will respond within 24 hours."
    
    # Update complaint with solution
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE complaints SET solution = ?, status = ? WHERE id = ?',
        (solution, 'resolved', complaint_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'solution': solution, 'complaint_id': complaint_id})

# Store conversation sessions in memory (in production, use a proper database)
conversation_sessions = {}

def get_user_orders_context(username, service, user_type, specific_order_id=None):
    """Get user's order history and context for AI processing"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get recent orders for this user and service
        cursor.execute("""
            SELECT id, service, status, price, restaurant_name, start_location, end_location, 
                   food_items, products_ordered, cab_type, date, payment_method, details
            FROM orders 
            WHERE username = ? AND service = ?
            ORDER BY date DESC 
            LIMIT 10
        """, (username, service))
        
        orders = cursor.fetchall()
        
        # Build context string
        orders_context = []
        
        # If specific order ID is provided, prioritize that order
        if specific_order_id:
            # First, get the specific order
            cursor.execute("""
                SELECT id, service, status, price, restaurant_name, start_location, end_location,
                       food_items, products_ordered, cab_type, date, payment_method, details
                FROM orders 
                WHERE id = ? AND username = ?
            """, (specific_order_id, username))
            
            specific_order = cursor.fetchone()
            
            if specific_order:
                orders_context.append(f"SPECIFIC ORDER COMPLAINT for {username}:")
                order_id, svc, status, price, restaurant, start_location, end_location, food_items, products_ordered, cab_type, date, payment, details = specific_order
                
                # Get the appropriate items field based on service
                items = food_items if food_items else (products_ordered if products_ordered else cab_type)
                address = end_location if end_location else start_location
                
                # Parse details safely
                details_obj = safe_json_loads(details) if details else {}
                
                order_info = f"- COMPLAINT ORDER {order_id}: {status.upper()}"
                if restaurant:
                    order_info += f" from {restaurant}"
                if price:
                    order_info += f" (${price:.2f})"
                if items:
                    order_info += f" - Items: {items}"
                if date:
                    order_info += f" on {date}"
                if address:
                    order_info += f" - Delivered to: {address}"
                
                # Add relevant details
                if details_obj.get('rating'):
                    order_info += f" (Rating: {details_obj['rating']}/5)"
                if details_obj.get('complaint'):
                    order_info += f" [Previous complaint: {details_obj['complaint']}]"
                if details_obj.get('cancelled_reason'):
                    order_info += f" [Cancelled: {details_obj['cancelled_reason']}]"
                    
                orders_context.append(order_info)
                orders_context.append(f"\nOTHER RECENT ORDERS for context:")
            else:
                orders_context.append(f"ERROR: Order {specific_order_id} not found for {username}")
                orders_context.append(f"CUSTOMER ORDER HISTORY for {username}:")
        else:
            orders_context.append(f"CUSTOMER ORDER HISTORY for {username}:")
        
        if orders:
            for order in orders:
                order_id, svc, status, price, restaurant, start_location, end_location, food_items, products_ordered, cab_type, date, payment, details = order
                
                # Get the appropriate items field based on service
                items = food_items if food_items else (products_ordered if products_ordered else cab_type)
                address = end_location if end_location else start_location
                
                # Skip the specific order if it's already highlighted above
                if specific_order_id and order_id == specific_order_id:
                    continue
                
                # Parse details safely
                details_obj = safe_json_loads(details) if details else {}
                
                order_info = f"- Order {order_id}: {status.upper()}"
                if restaurant:
                    order_info += f" from {restaurant}"
                if price:
                    order_info += f" (${price:.2f})"
                if items:
                    order_info += f" - Items: {items}"
                if date:
                    order_info += f" on {date}"
                
                # Add relevant details
                if details_obj.get('rating'):
                    order_info += f" (Rating: {details_obj['rating']}/5)"
                if details_obj.get('complaint'):
                    order_info += f" [Previous complaint: {details_obj['complaint']}]"
                if details_obj.get('cancelled_reason'):
                    order_info += f" [Cancelled: {details_obj['cancelled_reason']}]"
                    
                orders_context.append(order_info)
        else:
            orders_context.append(f"No previous orders found for {username} in {service}")
            
        # Get user credibility score
        cursor.execute("SELECT credibility_score FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        credibility = user_data[0] if user_data else 7
        
        orders_context.append(f"Customer credibility score: {credibility}/10")
        
        conn.close()
        return "\n".join(orders_context)
        
    except Exception as e:
        print(f"Error getting user orders context: {e}")
        return f"Unable to retrieve order history for {username}"

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot conversation"""
    data = request.json
    message = data.get('message', '').strip()
    service = data.get('service')
    user_type = data.get('user_type')
    conversation_id = data.get('conversation_id')
    category = data.get('category')
    sub_issue = data.get('sub_issue')
    username = data.get('username', 'anonymous')
    order_id = data.get('order_id')
    previous_messages = data.get('messages', [])
    
    if not message or not service or not user_type:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Initialize or get conversation session
    if conversation_id not in conversation_sessions:
        conversation_sessions[conversation_id] = {
            'service': service,
            'user_type': user_type,
            'username': username,
            'messages': [],
            'context': {},
            'current_issue': None,
            'awaiting_image': False,
            'category': category,
            'sub_issue': sub_issue
        }
    
    session = conversation_sessions[conversation_id]
    session['messages'].append({'role': 'user', 'content': message})
    
    try:
        print(f"DEBUG: Chat request - username={username}, category={category}, sub_issue={sub_issue}")
        
        # Fetch user's order data from database to provide context
        user_orders_context = get_user_orders_context(username, service, user_type, order_id)
        
        # If we have both category and sub_issue, use conversational AI processing
        if category and sub_issue:
            # Special handling for grab_cabs driver navigation route issue (direct handler call)
            if (service == 'grab_cabs' and user_type == 'driver' and 
                category == 'operational_problems' and sub_issue == 'handle_incorrect_navigation_route'):
                
                try:
                    from grab_cabs.driver.operational_problems import OperationalProblemsHandler
                    handler = OperationalProblemsHandler()
                    response_text = handler.handle_incorrect_navigation_route(message)
                    
                    session['messages'].append({'role': 'assistant', 'content': response_text})
                    
                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Handler call failed: {e}")
                    # Fall through to AI engine processing
            
            from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
            ai_engine = EnhancedAgenticAIEngine()
            
            # Build conversation context from previous messages
            conversation_context = ""
            for msg in session['messages']:
                role = "Customer" if msg['role'] == 'user' else "Agent"
                conversation_context += f"{role}: {msg['content']}\n"
            
            # Use conversational processing with order context
            response = ai_engine.process_conversation(
                message=message,
                service=service,
                user_type=user_type,
                conversation_history=session['messages'],
                session_context={
                    'category': category,
                    'sub_issue': sub_issue,
                    'conversation_context': conversation_context,
                    'username': username,
                    'user_orders': user_orders_context,
                    'specific_order_id': order_id
                }
            )
            
            session['messages'].append({'role': 'assistant', 'content': response.get('text', '')})
            session['current_issue'] = sub_issue
            
            return jsonify({
                'response': response.get('text', ''),
                'requires_image': response.get('requires_image', False),
                'image_request': response.get('image_request'),
                'conversation_id': conversation_id
            })
        
        else:
            # Fallback to conversation processing if no specific issue selected
            from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
            ai_engine = EnhancedAgenticAIEngine()
            
            # Process conversation with context
            response = ai_engine.process_conversation(
                message=message,
                service=service,
                user_type=user_type,
                conversation_history=session['messages'],
                session_context={**session['context'], 'username': username}
            )
            
            session['messages'].append({'role': 'assistant', 'content': response.get('text', '')})
            
            # Update session context based on response
            if 'requires_image' in response:
                session['awaiting_image'] = response['requires_image']
                session['current_issue'] = response.get('issue_type')
            
            return jsonify({
                'response': response.get('text', ''),
                'requires_image': response.get('requires_image', False),
                'image_request': response.get('image_request'),
                'conversation_id': conversation_id
            })
        
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        
        fallback_response = "I apologize, but I'm having trouble processing your request right now. Could you please rephrase your question or provide more details about your issue?"
        
        return jsonify({
            'response': fallback_response,
            'requires_image': False,
            'conversation_id': conversation_id
        })

@app.route('/api/chat/image', methods=['POST'])
def chat_image():
    """Handle image uploads in chat context"""
    data = request.json
    image_data = data.get('image_data')
    service = data.get('service')
    user_type = data.get('user_type')
    conversation_id = data.get('conversation_id')
    
    if not image_data or not conversation_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if conversation_id not in conversation_sessions:
        return jsonify({'error': 'Invalid conversation session'}), 400
    
    session = conversation_sessions[conversation_id]
    
    try:
        # Get user orders context
        username = session.get('username', 'anonymous')
        user_orders_context = get_user_orders_context(username, service, user_type)
        
        # Use the enhanced AI engine to process image
        from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
        ai_engine = EnhancedAgenticAIEngine()
        
        # If we have a specific issue, use direct processing
        if session.get('sub_issue'):
            # Get the last user message for context
            user_messages = [msg['content'] for msg in session['messages'] if msg['role'] == 'user']
            last_user_message = user_messages[-1] if user_messages else "Please help me with this issue"
            
            response_text = ai_engine.process_complaint(
                function_name=session['sub_issue'],
                user_query=last_user_message,
                service=service,
                user_type=user_type,
                image_data=image_data,
                username=session.get('username', 'anonymous')
            )
            
            session['messages'].append({'role': 'assistant', 'content': response_text})
            session['awaiting_image'] = False
            
            return jsonify({
                'response': response_text,
                'requires_image': False,
                'conversation_id': conversation_id
            })
        
        else:
            # Process image with conversation context
            response = ai_engine.process_conversation_image(
                image_data=image_data,
                service=service,
                user_type=user_type,
                conversation_history=session['messages'],
                current_issue=session.get('current_issue'),
                session_context={
                    **session['context'],
                    'user_orders': user_orders_context
                }
            )
            
            session['messages'].append({'role': 'assistant', 'content': response.get('text', '')})
            session['awaiting_image'] = False
            
            return jsonify({
                'response': response.get('text', ''),
                'requires_image': False,
                'conversation_id': conversation_id
            })
        
    except Exception as e:
        print(f"Chat image error: {e}")
        return jsonify({
            'response': "Thank you for uploading the image. I'm analyzing it now and will provide a solution shortly.",
            'requires_image': False,
            'conversation_id': conversation_id
        })

def generate_ai_solution(complaint_data):
    """Generate AI solution using the actual handler methods with image support"""
    import sys
    print(f"\n=== GENERATING AI SOLUTION ===", flush=True)
    print(f"Service: {complaint_data.get('service')}", flush=True)
    print(f"User Type: {complaint_data.get('user_type')}", flush=True)
    print(f"Sub Issue: {complaint_data.get('sub_issue')}", flush=True)
    print(f"Description: {complaint_data.get('description', '')[:100]}...", flush=True)
    print(f"Has Image: {bool(complaint_data.get('image_data'))}", flush=True)
    sys.stdout.flush()
    
    try:
        service = complaint_data['service']
        user_type = complaint_data['user_type']
        sub_issue = complaint_data['sub_issue']
        description = complaint_data['description']
        image_data = complaint_data.get('image_data')  # Optional image data
        
        user_type_folder = user_type if user_type != 'darkstore' else 'dark_house'
        category_handler = complaint_data['category']
        
        # Import the specific handler module
        # Special handling for grab_cabs driver with new handler structure
        if service == 'grab_cabs' and user_type == 'driver':
            # Map category_id to actual file names
            category_file_mapping = {
                'customer_experience': 'customer_experience',
                'driver_vehicle_issues': 'driver_vehicle_issues', 
                'fare_payment': 'fare_payment',
                'operational_issues': 'operational_issues',
                'operational_problems': 'operational_problems'
            }
            actual_file = category_file_mapping.get(category_handler, category_handler)
            module_path = f"{service}.{user_type_folder}.{actual_file}"
        else:
            module_path = f"{service}.{user_type_folder}.{category_handler}"
        
        try:
            handler_module = importlib.import_module(module_path)
            handler_classes = [getattr(handler_module, name) for name in dir(handler_module) 
                             if name.endswith('Handler') and not name.startswith('_')]
            
            if handler_classes:
                handler_class = handler_classes[0]
                handler_instance = handler_class()
                
                # Call the specific method if it exists
                if hasattr(handler_instance, sub_issue):
                    method = getattr(handler_instance, sub_issue)
                    # Check if method accepts image_data parameter
                    import inspect
                    sig = inspect.signature(method)
                    if 'image_data' in sig.parameters:
                        result = method(description, image_data=image_data)
                        print(f"AI Handler Result (with image): {result[:200] if result else 'None'}...")
                        if result and not result.startswith("Thank you for your complaint"):
                            return result
                        else:
                            print("AI returned generic fallback, trying direct AI call...")
                    else:
                        result = method(description)
                        print(f"AI Handler Result (text-only): {result[:200] if result else 'None'}...")
                        if result and not result.startswith("Thank you for your complaint"):
                            return result
                        else:
                            print("AI returned generic fallback, trying direct AI call...")
                else:
                    print(f"Method {sub_issue} not found in handler")
                    
                # If we reach here, try direct AI processing
                print("Attempting direct AI engine call...")
                from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
                ai_engine = EnhancedAgenticAIEngine()
                
                direct_result = ai_engine.process_complaint(
                    function_name=sub_issue,
                    user_query=description,
                    service=service,
                    user_type=user_type,
                    image_data=image_data
                )
                
                print(f"Direct AI Result: {direct_result[:200] if direct_result else 'None'}...")
                return direct_result
            else:
                print("No handler classes found - using direct AI")
            
        except ImportError as e:
            print(f"Import error: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"Handler execution error: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error generating AI solution: {e}")
    
    # If everything fails, use direct AI call
    print("All methods failed, trying final direct AI call...")
    try:
        from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
        ai_engine = EnhancedAgenticAIEngine()
        
        final_result = ai_engine.process_complaint(
            function_name=complaint_data['sub_issue'],
            user_query=complaint_data['description'],
            service=complaint_data['service'],
            user_type=complaint_data['user_type'],
            image_data=complaint_data.get('image_data')
        )
        
        if final_result and len(final_result) > 100:
            print(f"Final AI result successful: {len(final_result)} chars")
            return final_result
    except Exception as e:
        print(f"Final AI call failed: {e}")
    
    # Absolute fallback
    print("Using absolute fallback response")
    return f"Thank you for your complaint. We have received your issue regarding {complaint_data['description'][:100]}... and our team is working on a resolution. You will receive an update within 24 hours."

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=8000)