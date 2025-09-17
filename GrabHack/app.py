from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from models import GrabService, Actor, ACTOR_ISSUE_MAPPING, SERVICE_ACTORS, IssueCategory
from cross_actor_service import CrossActorUpdateService
import importlib

# Load environment variables from parent directory
load_dotenv(dotenv_path="../.env")

app = Flask(__name__)
CORS(app)

DATABASE_PATH = 'grabhack.db'

# Initialize cross-actor update service
cross_actor_service = CrossActorUpdateService(DATABASE_PATH)

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
    
    # Create orders table with coordinate-based location fields and update tracking
    cursor.execute('''
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            user_type TEXT NOT NULL,
            username TEXT NOT NULL,
            status TEXT NOT NULL,
            price REAL,
            start_latitude REAL,
            start_longitude REAL,
            start_address TEXT,
            end_latitude REAL,
            end_longitude REAL,
            end_address TEXT,
            customer_id TEXT,
            restaurant_id TEXT,
            driver_id TEXT,
            restaurant_name TEXT,
            food_items TEXT,
            cab_type TEXT,
            products_ordered TEXT,
            payment_method TEXT DEFAULT 'online',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            last_updated_by TEXT,
            last_update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_count INTEGER DEFAULT 0,
            current_status_remarks TEXT DEFAULT 'Order placed'
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

    # Create order_updates table for cross-actor update tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            actor_type TEXT NOT NULL,
            actor_username TEXT NOT NULL,
            update_type TEXT NOT NULL,
            description TEXT NOT NULL,
            details TEXT,
            affected_actors TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    # Create actor_notifications table for real-time notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actor_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            target_actor_type TEXT NOT NULL,
            target_username TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            source_update_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (source_update_id) REFERENCES order_updates(id)
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
    
    # Insert comprehensive demo orders for testing all scenarios with coordinate-based locations
    demo_orders = [
        # === GRAB FOOD CUSTOMER ORDERS ===
        # High credibility customer (customer1) - mostly successful orders
        ('GF001', 'grab_food', 'customer', 'customer1', 'completed', 25.50,
         12.9352, 77.6245, 'Pizza Palace Restaurant, Koramangala', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', 'REST001', 'DRV001', 'Pizza Palace', 'Margherita Pizza Large, Garlic Bread, Coca Cola', None, None,
         'online', '2024-08-15', '{"restaurant": "Pizza Palace", "total": 25.50, "rating": 5}'),

        ('GF002', 'grab_food', 'customer', 'customer1', 'completed', 32.75,
         12.9698, 77.7500, 'Burger Joint, Whitefield', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', 'REST002', 'DRV002', 'Burger Joint', 'Double Cheeseburger, Large Fries, Chocolate Milkshake', None, None,
         'upi', '2024-08-20', '{"restaurant": "Burger Joint", "total": 32.75, "rating": 4}'),

        ('GF003', 'grab_food', 'customer', 'customer1', 'completed', 18.90,
         12.9716, 77.5946, 'Taco Bell, MG Road', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', 'REST003', 'DRV003', 'Taco Bell', 'Crunchy Taco Supreme, Nachos, Pepsi', None, None,
         'card', '2024-09-01', '{"restaurant": "Taco Bell", "total": 18.90, "rating": 5}'),
        
        # Medium credibility customer (customer2) - mixed experience
        ('GF004', 'grab_food', 'customer', 'customer2', 'completed', 28.40,
         12.9141, 77.6023, 'Italian Bistro, Banashankari', 12.9698, 77.7500, '456 Pine Road House 12, Whitefield',
         'CUST002', 'REST004', 'DRV004', 'Italian Bistro', 'Chicken Alfredo, Caesar Salad, Garlic Bread', None, None,
         'cod', '2024-08-25', '{"restaurant": "Italian Bistro", "total": 28.40, "rating": 3}'),

        ('GF005', 'grab_food', 'customer', 'customer2', 'cancelled', 22.00,
         12.9279, 77.5946, 'Chinese Palace, Brigade Road', 12.9698, 77.7500, '456 Pine Road House 12, Whitefield',
         'CUST002', 'REST005', None, 'Chinese Palace', 'Sweet and Sour Chicken, Fried Rice', None, None,
         'online', '2024-09-02', '{"restaurant": "Chinese Palace", "total": 22.00, "cancelled_reason": "long_wait"}'),

        ('GF006', 'grab_food', 'customer', 'customer2', 'in_progress', 19.75,
         12.9698, 77.7500, 'Subway, Whitefield Main Road', 12.9698, 77.7500, '456 Pine Road House 12, Whitefield',
         'CUST002', 'REST006', 'DRV005', 'Subway', 'Chicken Teriyaki Footlong, Cookies, Orange Juice', None, None,
         'online', '2024-09-06', '{"restaurant": "Subway", "total": 19.75}'),
        
        # Low credibility customer (customer3) - frequent complaints
        ('GF007', 'grab_food', 'customer', 'customer3', 'completed', 31.20,
         12.9716, 77.5946, 'Premium Steakhouse, UB City Mall', 12.9141, 77.6023, '789 Elm Avenue Floor 3, Banashankari',
         'CUST003', 'REST007', 'DRV006', 'Premium Steakhouse', 'Ribeye Steak, Mashed Potatoes, Wine', None, None,
         'card', '2024-08-30', '{"restaurant": "Premium Steakhouse", "total": 31.20, "rating": 2, "complaint": "food_cold"}'),

        ('GF008', 'grab_food', 'customer', 'customer3', 'cancelled', 15.50,
         12.9716, 77.5946, 'Fast Food Corner, Brigade Road', 12.9141, 77.6023, '789 Elm Avenue Floor 3, Banashankari',
         'CUST003', 'REST008', None, 'Fast Food Corner', 'Chicken Nuggets, Fries', None, None,
         'cod', '2024-09-03', '{"restaurant": "Fast Food Corner", "total": 15.50, "cancelled_reason": "address_wrong"}'),

        # Good customer (john_doe)
        ('GF009', 'grab_food', 'customer', 'john_doe', 'completed', 45.80,
         12.9352, 77.6245, 'Sushi World, Koramangala', 12.9352, 77.6245, '321 Maple Drive Apartment 8A, Koramangala',
         'CUST004', 'REST009', 'DRV007', 'Sushi World', 'California Roll, Salmon Sashimi, Miso Soup, Green Tea', None, None,
         'online', '2024-09-05', '{"restaurant": "Sushi World", "total": 45.80, "rating": 5}'),

        # Average customer (jane_smith)
        ('GF010', 'grab_food', 'customer', 'jane_smith', 'completed', 27.30,
         12.9279, 77.6271, 'Mediterranean Grill, Jayanagar', 12.9279, 77.6271, '654 Cedar Lane House 5, Jayanagar',
         'CUST005', 'REST010', 'DRV008', 'Mediterranean Grill', 'Chicken Shawarma, Hummus, Pita Bread, Lemonade', None, None,
         'upi', '2024-09-04', '{"restaurant": "Mediterranean Grill", "total": 27.30, "rating": 4}'),
         
        # === GRAB EXPRESS CUSTOMER ORDERS ===
        # High credibility customer (customer1) - express delivery orders
        ('GE001', 'grab_express', 'customer', 'customer1', 'completed', 12.50,
         12.9716, 77.5946, 'Electronics Store Downtown, MG Road', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', None, 'EXP001', None, None, None, 'Smartphone Case, Screen Protector, Charging Cable',
         'online', '2024-09-01', '{"pickup_location": "Electronics Store Downtown", "delivery_time_minutes": 45, "vehicle_type": "Bike", "package_size": "Small", "rating": 5}'),

        ('GE002', 'grab_express', 'customer', 'customer1', 'completed', 25.80,
         12.9698, 77.7500, 'Office Supply Center, Whitefield', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', None, 'EXP002', None, None, None, 'Laptop Stand, Wireless Mouse, Notebook Set',
         'card', '2024-09-03', '{"pickup_location": "Office Supply Center", "delivery_time_minutes": 60, "vehicle_type": "Car", "package_size": "Medium", "rating": 4}'),

        ('GE003', 'grab_express', 'customer', 'customer1', 'in_progress', 35.00,
         13.0827, 80.2707, 'Furniture Warehouse, Electronic City', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', None, 'EXP003', None, None, None, 'Office Chair (Disassembled), Desk Lamp',
         'cod', '2024-09-06', '{"pickup_location": "Furniture Warehouse", "estimated_delivery_minutes": 90, "vehicle_type": "Truck", "package_size": "Large", "special_instructions": "Fragile - Handle with care"}'),
        
        # === GRAB FOOD DELIVERY AGENT ORDERS ===
        ('GF011', 'grab_food', 'delivery_agent', 'agent1', 'assigned', 0.00,
         12.9352, 77.6245, 'Pizza Palace, Koramangala', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         None, 'REST001', 'agent1', 'Pizza Palace', 'Pickup Order GF001', None, None,
         'online', '2024-09-06', '{"assigned_order": "GF001", "pickup_time": "19:30", "estimated_delivery": "20:00"}'),

        ('GF012', 'grab_food', 'delivery_agent', 'agent2', 'delivering', 0.00,
         12.9698, 77.7500, 'Burger Joint, Whitefield', 12.9698, 77.7500, '456 Pine Road House 12, Whitefield',
         None, 'REST002', 'agent2', 'Burger Joint', 'Delivery in Progress Order GF006', None, None,
         'cod', '2024-09-06', '{"assigned_order": "GF006", "pickup_time": "20:15", "gps_issues": "true"}'),

        ('GF013', 'grab_food', 'delivery_agent', 'agent3', 'completed', 0.00,
         12.9141, 77.6023, 'Italian Bistro, Banashankari', 12.9141, 77.6023, '789 Elm Avenue Floor 3, Banashankari',
         None, 'REST004', 'agent3', 'Italian Bistro', 'Completed Delivery GF007', None, None,
         'online', '2024-09-05', '{"assigned_order": "GF007", "delivery_time": "21:45", "customer_rating": 5}'),
         
        # === GRAB FOOD RESTAURANT ORDERS ===
        ('GF014', 'grab_food', 'restaurant', 'resto1', 'preparing', 0.00,
         12.9352, 77.6245, 'Pizza Palace Kitchen, Koramangala', 12.9352, 77.6245, 'Preparation Area, Koramangala',
         None, 'resto1', None, 'Pizza Palace Kitchen', 'Preparing Order GF001 - Margherita Pizza', None, None,
         'online', '2024-09-06', '{"preparing_order": "GF001", "items": 3, "prep_time_minutes": 25}'),

        ('GF015', 'grab_food', 'restaurant', 'resto2', 'ready', 0.00,
         12.9698, 77.7500, 'Burger Joint Kitchen, Whitefield', 12.9698, 77.7500, 'Pickup Counter, Whitefield',
         None, 'resto2', None, 'Burger Joint Kitchen', 'Order Ready GF006 - Awaiting Pickup', None, None,
         'cod', '2024-09-06', '{"ready_order": "GF006", "items": 3, "waiting_time_minutes": 15, "ingredients_shortage": "pickles"}'),

        ('GF016', 'grab_food', 'restaurant', 'resto3', 'delayed', 0.00,
         12.9141, 77.6023, 'Italian Bistro Kitchen, Banashankari', 12.9141, 77.6023, 'Preparation Area, Banashankari',
         None, 'resto3', None, 'Italian Bistro Kitchen', 'Delayed Order GF004 - High Volume', None, None,
         'online', '2024-09-06', '{"delayed_order": "GF004", "delay_reason": "high_volume", "estimated_delay_minutes": 30}'),
        
        # === GRAB CABS ORDERS ===
        # Customer cab orders
        ('GC001', 'grab_cabs', 'customer', 'customer1', 'completed', 15.00,
         12.9716, 77.5946, 'Forum Mall, Koramangala', 13.1986, 77.7066, 'Kempegowda International Airport',
         'CUST001', None, 'DRV101', None, None, 'Sedan', None,
         'upi', '2024-09-02', '{"from": "Forum Mall", "to": "Airport", "distance_km": 35, "duration_minutes": 55}'),

        ('GC002', 'grab_cabs', 'customer', 'john_doe', 'in_progress', 8.50,
         12.9767, 77.5993, 'Bangalore City Railway Station', 12.9716, 77.5946, 'UB City Mall, MG Road',
         'CUST004', None, 'DRV102', None, None, 'Hatchback', None,
         'online', '2024-09-06', '{"from": "Railway Station", "to": "Business District", "driver_name": "Alex Kumar"}'),

        # Driver orders
        ('GC003', 'grab_cabs', 'driver', 'driver1', 'active', 12.75,
         12.9716, 77.5946, 'MG Road Metro Station', 12.8438, 77.6606, 'Residential Complex, Bannerghatta',
         'CUST006', None, 'driver1', None, None, 'SUV', None,
         'cod', '2024-09-06', '{"passenger": "Sarah Wilson", "pickup": "MG Road", "destination": "Bannerghatta"}'),
         
        ('GC004', 'grab_cabs', 'driver', 'driver2', 'completed', 22.30,
         12.9716, 77.5946, 'Hotel Grand Plaza, UB City', 12.9352, 77.6245, 'Forum Mall, Koramangala',
         'CUST007', None, 'driver2', None, None, 'Sedan', None,
         'card', '2024-09-05', '{"passenger": "Mike Johnson", "trip_rating": 5, "tip_amount": 2.50}'),
        
        # === GRAB MART ORDERS ===
        # Customer grocery orders
        ('GM001', 'grab_mart', 'customer', 'customer1', 'completed', 67.80,
         12.9279, 77.6271, 'FreshMart Store, Jayanagar', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', 'STORE001', 'DRV201', None, None, None, 'Milk, Bread, Eggs, Fruits, Vegetables, Cheese, Yogurt',
         'card', '2024-09-03', '{"store": "FreshMart", "items": 15, "total": 67.80, "delivery_instructions": "Leave at door"}'),
         
        ('GM002', 'grab_mart', 'customer', 'jane_smith', 'in_progress', 43.20,
         12.9698, 77.7500, 'SuperMart, Whitefield', 12.9279, 77.6271, '654 Cedar Lane House 5, Jayanagar',
         'CUST005', 'STORE002', 'DRV202', None, None, None, 'Rice, Cooking Oil, Spices, Onions, Potatoes, Chicken',
         'online', '2024-09-06', '{"store": "SuperMart", "items": 12, "special_instructions": "Call before delivery"}'),
         
        # Dark store orders
        ('GM003', 'grab_mart', 'dark_house', 'store1', 'picking', 58.90,
         12.9279, 77.6271, 'Dark Store Warehouse A, Jayanagar', 12.9352, 77.6245, 'Customer Delivery Zone, Koramangala',
         'CUST008', 'STORE001', None, None, None, None, 'Frozen Foods, Dairy Products, Snacks, Beverages',
         'cod', '2024-09-06', '{"picking_order": "GM002", "items_picked": 8, "items_remaining": 4, "picker_id": "PICK001"}'),

        # More grab_express orders for variety
        ('GE004', 'grab_express', 'customer', 'john_doe', 'completed', 18.90,
         12.9352, 77.6245, 'Medical Pharmacy, Koramangala', 12.9352, 77.6245, '321 Maple Drive Apartment 8A, Koramangala',
         'CUST004', None, 'EXP004', None, None, None, 'Prescription Medicines, Medical Supplies',
         'online', '2024-09-02', '{"pickup_location": "Medical Pharmacy", "delivery_time_minutes": 30, "vehicle_type": "Bike", "package_size": "Small", "urgent_delivery": true, "rating": 5}')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO orders
        (id, service, user_type, username, status, price, start_latitude, start_longitude, start_address,
         end_latitude, end_longitude, end_address, customer_id, restaurant_id, driver_id, restaurant_name,
         food_items, cab_type, products_ordered, payment_method, date, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        SELECT id, service, user_type, username, status, price, start_latitude, start_longitude, start_address,
               end_latitude, end_longitude, end_address, customer_id, restaurant_id, driver_id, restaurant_name,
               food_items, cab_type, products_ordered, payment_method, date, details
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
            'start_latitude': row[6],
            'start_longitude': row[7],
            'start_address': row[8],
            'end_latitude': row[9],
            'end_longitude': row[10],
            'end_address': row[11],
            'customer_id': row[12],
            'restaurant_id': row[13],
            'driver_id': row[14],
            'restaurant_name': row[15],
            'food_items': row[16],
            'cab_type': row[17],
            'products_ordered': row[18],
            'payment_method': row[19],
            'date': row[20],
            'details': safe_json_loads(row[21])
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
                {'id': 'ride_experience_handler', 'name': 'Ride Experience'},
                {'id': 'driver_harassment', 'name': 'Driver Harassment & Safety'},
                {'id': 'app_booking_issues', 'name': 'App/Booking Issues'},
                {'id': 'cancellation_refund', 'name': 'Cancellation/Refund Policy'},
                {'id': 'airport_problems', 'name': 'Airport Booking Problems'}
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

        # Special handling for grab_cabs customer issues
        if service == 'grab_cabs' and user_type == 'customer':
            sub_issues = []

            if category_id == 'ride_experience_handler':
                sub_issues = [
                    {'id': 'handle_unsafe_driving_behavior', 'name': 'Unsafe Driving Behavior', 'description': 'Report rash driving, speeding, or dangerous behavior'},
                    {'id': 'handle_vehicle_problems', 'name': 'Vehicle Condition Issues', 'description': 'Report dirty, damaged, or malfunctioning vehicles'},
                    {'id': 'handle_accidents_during_ride', 'name': 'Accidents During Ride', 'description': 'Report accidents or damage that occurred during your trip'}
                ]
            elif category_id == 'driver_harassment':
                sub_issues = [
                    {'id': 'handle_driver_harassment_complaint', 'name': 'Driver Harassment/Rude Behavior', 'description': 'Report inappropriate driver behavior'}
                ]
            elif category_id == 'app_booking_issues':
                sub_issues = [
                    {'id': 'handle_app_booking_issues', 'name': 'App/Booking Technical Issues', 'description': 'Payment, tracking, or app malfunction problems'}
                ]
            elif category_id == 'cancellation_refund':
                sub_issues = [
                    {'id': 'handle_cancellation_refund_policy_complications', 'name': 'Cancellation/Refund Policy Issues', 'description': 'Issues with cancellation or refund policies'}
                ]
            elif category_id == 'airport_problems':
                sub_issues = [
                    {'id': 'handle_airport_booking_problems', 'name': 'Airport Booking Problems', 'description': 'Missed flights or incorrect sync issues'}
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
            username=data.get('username', 'anonymous'),
            order_id=data.get('order_id')
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

@app.route('/api/missing-items', methods=['POST'])
def missing_items():
    """Dedicated endpoint for missing items with interactive selection"""
    data = request.json
    username = data.get('username', 'anonymous')
    order_id = data.get('order_id')
    message = data.get('message', 'Missing items complaint')

    print(f"DEBUG: Missing items endpoint called - username={username}, order_id={order_id}")

    try:
        # Get actual order data from database directly in Flask app
        actual_order_data = get_actual_order_data_direct(username, order_id)
        if not actual_order_data:
            return jsonify({
                'response': "❌ Unable to find your order details. Please provide your order ID or contact support.",
                'requires_image': False,
                'success': False
            })

        # Generate the interactive selection interface
        response_text = generate_missing_items_selection_interface(actual_order_data)

        print(f"DEBUG: Generated selection interface with {len(response_text)} characters")

        return jsonify({
            'response': response_text,
            'requires_image': False,
            'success': True
        })

    except Exception as e:
        print(f"ERROR: Missing items handler failed: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'response': f"Sorry, I encountered an error processing your missing items request. Please try again or contact support. Error: {str(e)}",
            'requires_image': False,
            'success': False
        })

def get_actual_order_data_direct(username: str, order_id: str = None) -> dict:
    """Get actual order data from database - Flask app version"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get order data - use order_id if provided, otherwise get most recent
        if order_id:
            cursor.execute('''
                SELECT id, food_items, restaurant_name, price, status, date
                FROM orders
                WHERE id = ? AND username = ? AND service = 'grab_food' AND user_type = 'customer'
            ''', (order_id, username))
        else:
            cursor.execute('''
                SELECT id, food_items, restaurant_name, price, status, date
                FROM orders
                WHERE username = ? AND service = 'grab_food' AND user_type = 'customer'
                ORDER BY date DESC LIMIT 1
            ''', (username,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        order_id, food_items, restaurant_name, price, status, date = result

        # Parse food items into a list
        if food_items:
            # Split by common delimiters and clean up
            items_list = []
            for item in food_items.replace(',', '\n').replace(';', '\n').split('\n'):
                item = item.strip()
                if item:
                    items_list.append(item)
        else:
            items_list = []

        # Format items for display
        formatted_items = '\n'.join([f"• {item}" for item in items_list])

        return {
            'order_id': order_id,
            'food_items_list': items_list,
            'formatted_items': formatted_items,
            'restaurant_name': restaurant_name,
            'price': price,
            'status': status,
            'date': date,
            'total_items_count': len(items_list)
        }

    except Exception as e:
        print(f"Error getting order data: {e}")
        return None

def generate_missing_items_selection_interface(actual_order_data: dict) -> str:
    """Generate interactive missing items selection interface"""
    order_id = actual_order_data['order_id']
    restaurant = actual_order_data['restaurant_name']
    items_list = actual_order_data['food_items_list']

    # Create interactive selection format
    items_with_checkboxes = []
    for i, item in enumerate(items_list, 1):
        items_with_checkboxes.append(f"☐ {i}. {item}")

    return f"""🔍 **Missing Items Selection**

**Your Order:** {order_id} from {restaurant}
**Status:** {actual_order_data.get('status', 'completed')}

**📝 Which items are missing from your order?**

{chr(10).join(items_with_checkboxes)}

**💡 How to select missing items:**
- **"Items 1 and 3 are missing"** - Select by numbers
- **"I didn't receive the {items_list[0] if items_list else 'first item'}"** - Select by name
- **"Missing items 2, 4, and 5"** - Multiple items
- **"All items are present"** - Nothing missing

**📷 Tip:** Upload a photo for AI-assisted selection!

**Select your missing items above and I'll process your refund immediately!**"""

# Store conversation sessions in memory (in production, use a proper database)
conversation_sessions = {}

def get_user_orders_context(username, service, user_type, specific_order_id=None):
    """Get user's order history and context for AI processing"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get recent orders for this user and service
        cursor.execute("""
            SELECT id, service, status, price, restaurant_name, start_latitude, start_longitude, start_address,
                   end_latitude, end_longitude, end_address, food_items, products_ordered, cab_type, date, payment_method, details
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
                SELECT id, service, status, price, restaurant_name, start_latitude, start_longitude, start_address,
                       end_latitude, end_longitude, end_address, food_items, products_ordered, cab_type, date, payment_method, details
                FROM orders
                WHERE id = ? AND username = ?
            """, (specific_order_id, username))

            specific_order = cursor.fetchone()

            if specific_order:
                orders_context.append(f"SPECIFIC ORDER COMPLAINT for {username}:")
                order_id, svc, status, price, restaurant, start_lat, start_lng, start_addr, end_lat, end_lng, end_addr, food_items, products_ordered, cab_type, date, payment, details = specific_order

                # Get the appropriate items field based on service
                items = food_items if food_items else (products_ordered if products_ordered else cab_type)
                address = end_addr if end_addr else start_addr
                
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
                order_id, svc, status, price, restaurant, start_lat, start_lng, start_addr, end_lat, end_lng, end_addr, food_items, products_ordered, cab_type, date, payment, details = order

                # Get the appropriate items field based on service
                items = food_items if food_items else (products_ordered if products_ordered else cab_type)
                address = end_addr if end_addr else start_addr
                
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
    print("DEBUG: Chat endpoint called")
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
            'sub_issue': sub_issue,
            'order_id': order_id
        }
    
    session = conversation_sessions[conversation_id]
    session['messages'].append({'role': 'user', 'content': message})
    
    try:
        print(f"DEBUG: Chat request - username={username}, category={category}, sub_issue={sub_issue}")
        
        # Fetch user's order data from database to provide context
        user_orders_context = get_user_orders_context(username, service, user_type, order_id)
        
        # If we have both category and sub_issue, use conversational AI processing
        print(f"DEBUG: Chat request params - service={service}, user_type={user_type}, category={category}, sub_issue={sub_issue}")
        if category and sub_issue:
            # Special handling for grab_food customer missing items (direct handler call for interactive selection)
            print(f"DEBUG: Checking conditions - grab_food: {service == 'grab_food'}, customer: {user_type == 'customer'}, handle_missing_items: {sub_issue == 'handle_missing_items'}")
            if (service == 'grab_food' and user_type == 'customer' and
                sub_issue == 'handle_missing_items'):

                print(f"DEBUG: Direct missing items handler called - username={username}, order_id={order_id}")
                try:
                    from grab_food.customer.order_quality_handler import OrderQualityHandler
                    handler = OrderQualityHandler()
                    response_text = handler.handle_missing_items(
                        query=message,
                        image_data=None,  # Will be handled in image upload endpoint
                        username=username,
                        order_id=order_id
                    )

                    print(f"DEBUG: Handler response length: {len(response_text) if response_text else 0}")
                    session['messages'].append({'role': 'assistant', 'content': response_text})

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,  # Our handler now handles image requests internally
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Missing items handler call failed: {e}")
                    import traceback
                    traceback.print_exc()
                    # Fall through to AI engine processing

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

            # Special handling for grab_cabs customer driver harassment (hybrid workflow)
            if (service == 'grab_cabs' and user_type == 'customer' and
                category == 'driver_harassment' and sub_issue == 'handle_driver_harassment_complaint'):

                try:
                    from grab_cabs.customer.customer_experience import CustomerExperienceHandler
                    handler = CustomerExperienceHandler()

                    # Determine workflow stage and harassment type
                    harassment_type = None
                    workflow_stage = "initial"

                    # Check if this is a harassment type selection
                    message_lower = message.lower()
                    if 'threats' in message_lower:
                        harassment_type = 'Threats'
                        workflow_stage = "type_selected"
                    elif 'verbal abuse' in message_lower:
                        harassment_type = 'Verbal Abuse'
                        workflow_stage = "type_selected"
                    elif 'physical abuse' in message_lower:
                        harassment_type = 'Physical Abuse'
                        workflow_stage = "type_selected"
                    elif 'stalking' in message_lower:
                        harassment_type = 'Stalking'
                        workflow_stage = "type_selected"
                    elif 'inappropriate' in message_lower:
                        harassment_type = 'Inappropriate Behaviour'
                        workflow_stage = "type_selected"
                    else:
                        # Check if user already selected a type and is now providing description
                        prev_messages = session.get('messages', [])
                        for prev_msg in reversed(prev_messages):
                            if prev_msg.get('role') == 'assistant' and 'harassment report -' in prev_msg.get('content', '').lower():
                                # Extract harassment type from previous message
                                content = prev_msg.get('content', '')
                                if 'Threats' in content:
                                    harassment_type = 'Threats'
                                elif 'Verbal Abuse' in content:
                                    harassment_type = 'Verbal Abuse'
                                elif 'Physical Abuse' in content:
                                    harassment_type = 'Physical Abuse'
                                elif 'Stalking' in content:
                                    harassment_type = 'Stalking'
                                elif 'Inappropriate Behaviour' in content:
                                    harassment_type = 'Inappropriate Behaviour'

                                if harassment_type:
                                    # Check if user wants to upload photo or said no evidence
                                    if 'photo' in message.lower() or 'image' in message.lower() or 'evidence' in message.lower():
                                        if 'no evidence' in message.lower():
                                            workflow_stage = "ai_processing"
                                        else:
                                            workflow_stage = "image_request"
                                    else:
                                        # After text description, show image request
                                        workflow_stage = "image_request"
                                break

                    response_text = handler.handle_driver_harassment_complaint(
                        query=message,
                        harassment_type=harassment_type,
                        workflow_stage=workflow_stage
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})

                    # Store harassment_type in session for image processing
                    if harassment_type:
                        session['harassment_type'] = harassment_type

                    # Set requires_image to True when showing image upload prompt
                    requires_image = workflow_stage == "image_request"

                    return jsonify({
                        'response': response_text,
                        'requires_image': requires_image,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Driver harassment handler call failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs customer app/booking issues (hybrid workflow)
            if (service == 'grab_cabs' and user_type == 'customer' and
                category == 'app_booking_issues' and sub_issue == 'handle_app_booking_issues'):

                try:
                    from grab_cabs.customer.customer_experience import CustomerExperienceHandler
                    handler = CustomerExperienceHandler()

                    # Determine workflow stage and issue type
                    issue_type = None
                    workflow_stage = "initial"

                    message_lower = message.lower()
                    if 'payment problems' in message_lower:
                        issue_type = 'Payment Problems'
                        workflow_stage = "type_selected"
                    elif 'app crashes' in message_lower or 'freezing' in message_lower:
                        issue_type = 'App Crashes/Freezing'
                        workflow_stage = "type_selected"
                    elif 'gps' in message_lower or 'tracking' in message_lower:
                        issue_type = 'GPS/Tracking Issues'
                        workflow_stage = "type_selected"
                    elif 'booking failed' in message_lower:
                        issue_type = 'Booking Failed'
                        workflow_stage = "type_selected"
                    elif 'wrong fare' in message_lower or 'fare calculation' in message_lower:
                        issue_type = 'Wrong Fare Calculation'
                        workflow_stage = "type_selected"
                    else:
                        # Check if user already selected a type and is now providing description
                        prev_messages = session.get('messages', [])
                        for prev_msg in reversed(prev_messages):
                            if prev_msg.get('role') == 'assistant' and 'app/booking issues -' in prev_msg.get('content', '').lower():
                                content = prev_msg.get('content', '')
                                if 'Payment Problems' in content:
                                    issue_type = 'Payment Problems'
                                elif 'App Crashes/Freezing' in content:
                                    issue_type = 'App Crashes/Freezing'
                                elif 'GPS/Tracking Issues' in content:
                                    issue_type = 'GPS/Tracking Issues'
                                elif 'Booking Failed' in content:
                                    issue_type = 'Booking Failed'
                                elif 'Wrong Fare Calculation' in content:
                                    issue_type = 'Wrong Fare Calculation'

                                if issue_type:
                                    workflow_stage = "ai_processing"
                                break

                    response_text = handler.handle_app_booking_issues(
                        query=message,
                        issue_type=issue_type,
                        workflow_stage=workflow_stage
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"App booking handler call failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs customer cancellation/refund issues (hybrid workflow)
            if (service == 'grab_cabs' and user_type == 'customer' and
                category == 'cancellation_refund' and sub_issue == 'handle_cancellation_refund_policy_complications'):

                try:
                    from grab_cabs.customer.customer_experience import CustomerExperienceHandler
                    handler = CustomerExperienceHandler()

                    # Determine workflow stage and issue type
                    issue_type = None
                    workflow_stage = "initial"

                    message_lower = message.lower()
                    if 'unfair cancellation fee' in message_lower:
                        issue_type = 'Unfair Cancellation Fee'
                        workflow_stage = "type_selected"
                    elif 'refund not processed' in message_lower:
                        issue_type = 'Refund Not Processed'
                        workflow_stage = "type_selected"
                    elif 'refund amount incorrect' in message_lower:
                        issue_type = 'Refund Amount Incorrect'
                        workflow_stage = "type_selected"
                    elif 'policy not explained' in message_lower:
                        issue_type = 'Policy Not Explained Clearly'
                        workflow_stage = "type_selected"
                    elif 'unable to cancel' in message_lower:
                        issue_type = 'Unable to Cancel Ride'
                        workflow_stage = "type_selected"
                    else:
                        # Check previous messages for issue type
                        prev_messages = session.get('messages', [])
                        for prev_msg in reversed(prev_messages):
                            if prev_msg.get('role') == 'assistant' and 'cancellation/refund policy -' in prev_msg.get('content', '').lower():
                                content = prev_msg.get('content', '')
                                if 'Unfair Cancellation Fee' in content:
                                    issue_type = 'Unfair Cancellation Fee'
                                elif 'Refund Not Processed' in content:
                                    issue_type = 'Refund Not Processed'
                                elif 'Refund Amount Incorrect' in content:
                                    issue_type = 'Refund Amount Incorrect'
                                elif 'Policy Not Explained Clearly' in content:
                                    issue_type = 'Policy Not Explained Clearly'
                                elif 'Unable to Cancel Ride' in content:
                                    issue_type = 'Unable to Cancel Ride'

                                if issue_type:
                                    workflow_stage = "ai_processing"
                                break

                    response_text = handler.handle_cancellation_refund_policy_complications(
                        query=message,
                        issue_type=issue_type,
                        workflow_stage=workflow_stage
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Cancellation/refund handler call failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs customer airport issues (hybrid workflow)
            if (service == 'grab_cabs' and user_type == 'customer' and
                category == 'airport_problems' and sub_issue == 'handle_airport_booking_problems'):

                try:
                    from grab_cabs.customer.customer_experience import CustomerExperienceHandler
                    handler = CustomerExperienceHandler()

                    # Determine workflow stage and issue type
                    issue_type = None
                    workflow_stage = "initial"

                    message_lower = message.lower()
                    if 'missed flight' in message_lower or 'late driver' in message_lower:
                        issue_type = 'Missed Flight Due to Late Driver'
                        workflow_stage = "type_selected"
                    elif 'wrong terminal' in message_lower or 'wrong airport' in message_lower:
                        issue_type = 'Wrong Terminal/Airport'
                        workflow_stage = "type_selected"
                    elif 'flight sync' in message_lower:
                        issue_type = 'Flight Sync Issues'
                        workflow_stage = "type_selected"
                    elif 'airport pickup' in message_lower:
                        issue_type = 'Airport Pickup Problems'
                        workflow_stage = "type_selected"
                    elif 'flight delay' in message_lower:
                        issue_type = 'Flight Delay Complications'
                        workflow_stage = "type_selected"
                    else:
                        # Check previous messages for issue type
                        prev_messages = session.get('messages', [])
                        for prev_msg in reversed(prev_messages):
                            if prev_msg.get('role') == 'assistant' and 'airport booking problems -' in prev_msg.get('content', '').lower():
                                content = prev_msg.get('content', '')
                                if 'Missed Flight Due to Late Driver' in content:
                                    issue_type = 'Missed Flight Due to Late Driver'
                                elif 'Wrong Terminal/Airport' in content:
                                    issue_type = 'Wrong Terminal/Airport'
                                elif 'Flight Sync Issues' in content:
                                    issue_type = 'Flight Sync Issues'
                                elif 'Airport Pickup Problems' in content:
                                    issue_type = 'Airport Pickup Problems'
                                elif 'Flight Delay Complications' in content:
                                    issue_type = 'Flight Delay Complications'

                                if issue_type:
                                    workflow_stage = "ai_processing"
                                break

                    response_text = handler.handle_airport_booking_problems(
                        query=message,
                        issue_type=issue_type,
                        workflow_stage=workflow_stage
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Airport booking handler call failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs driver passenger harassment (hybrid workflow)
            if (service == 'grab_cabs' and user_type == 'driver' and
                category == 'customer_experience' and sub_issue == 'handle_passenger_harassment_complaint'):

                try:
                    from grab_cabs.driver.customer_experience import CustomerExperienceHandler
                    handler = CustomerExperienceHandler()

                    # Determine workflow stage and harassment type
                    harassment_type = None
                    workflow_stage = "initial"

                    # Check if this is a harassment type selection
                    message_lower = message.lower()
                    if 'threats' in message_lower:
                        harassment_type = 'Threats'
                        workflow_stage = "type_selected"
                    elif 'verbal abuse' in message_lower:
                        harassment_type = 'Verbal Abuse'
                        workflow_stage = "type_selected"
                    elif 'physical abuse' in message_lower:
                        harassment_type = 'Physical Abuse'
                        workflow_stage = "type_selected"
                    elif 'stalking' in message_lower:
                        harassment_type = 'Stalking'
                        workflow_stage = "type_selected"
                    elif 'inappropriate' in message_lower:
                        harassment_type = 'Inappropriate Behaviour'
                        workflow_stage = "type_selected"
                    else:
                        # Check if user already selected a type and is now providing description
                        prev_messages = session.get('messages', [])
                        for prev_msg in reversed(prev_messages):
                            if prev_msg.get('role') == 'assistant' and 'harassment report -' in prev_msg.get('content', '').lower():
                                # Extract harassment type from previous message
                                content = prev_msg.get('content', '')
                                if 'Threats' in content:
                                    harassment_type = 'Threats'
                                elif 'Verbal Abuse' in content:
                                    harassment_type = 'Verbal Abuse'
                                elif 'Physical Abuse' in content:
                                    harassment_type = 'Physical Abuse'
                                elif 'Stalking' in content:
                                    harassment_type = 'Stalking'
                                elif 'Inappropriate Behaviour' in content:
                                    harassment_type = 'Inappropriate Behaviour'

                                if harassment_type:
                                    # Check if user wants to upload photo or said no evidence
                                    if 'photo' in message.lower() or 'image' in message.lower() or 'evidence' in message.lower():
                                        if 'no evidence' in message.lower():
                                            workflow_stage = "ai_processing"
                                        else:
                                            workflow_stage = "image_request"
                                    else:
                                        # After text description, show image request
                                        workflow_stage = "image_request"
                                break

                    response_text = handler.handle_passenger_harassment_complaint(
                        query=message,
                        harassment_type=harassment_type,
                        workflow_stage=workflow_stage
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})

                    # Store harassment_type in session for image processing
                    if harassment_type:
                        session['harassment_type'] = harassment_type

                    # Set requires_image to True when showing image upload prompt
                    requires_image = workflow_stage == "image_request"

                    return jsonify({
                        'response': response_text,
                        'requires_image': requires_image,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Passenger harassment handler call failed: {e}")
                    # Fall through to AI engine processing

            from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
            ai_engine = EnhancedAgenticAIEngine()
            print(f"DEBUG: Using AI engine for conversation - service={service}, sub_issue={sub_issue}")
            
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
            last_user_message = user_messages[-1] if user_messages else "Image uploaded for missing items analysis"

            # Special handling for grab_food customer missing items with image
            if (service == 'grab_food' and user_type == 'customer' and
                session.get('sub_issue') == 'handle_missing_items'):

                try:
                    from grab_food.customer.order_quality_handler import OrderQualityHandler
                    handler = OrderQualityHandler()
                    response_text = handler.handle_missing_items(
                        query=last_user_message,
                        image_data=image_data,
                        username=session.get('username', 'anonymous'),
                        order_id=session.get('order_id')
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})
                    session['awaiting_image'] = False

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Missing items image handler failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs customer harassment with image
            elif (service == 'grab_cabs' and user_type == 'customer' and
                  session.get('sub_issue') == 'handle_driver_harassment_complaint'):

                try:
                    from grab_cabs.customer.customer_experience import CustomerExperienceHandler
                    handler = CustomerExperienceHandler()

                    # Extract harassment type from session or messages
                    harassment_type = session.get('harassment_type')
                    if not harassment_type:
                        # Try to extract from conversation history
                        for msg in reversed(session.get('messages', [])):
                            if 'harassment report -' in msg.get('content', '').lower():
                                content = msg.get('content', '')
                                if 'Verbal Abuse' in content:
                                    harassment_type = 'Verbal Abuse'
                                elif 'Physical Abuse' in content:
                                    harassment_type = 'Physical Abuse'
                                elif 'Threats' in content:
                                    harassment_type = 'Threats'
                                elif 'Stalking' in content:
                                    harassment_type = 'Stalking'
                                elif 'Inappropriate Behaviour' in content:
                                    harassment_type = 'Inappropriate Behaviour'
                                break

                    response_text = handler.handle_driver_harassment_complaint(
                        query=last_user_message,
                        harassment_type=harassment_type,
                        image_data=image_data,
                        workflow_stage="ai_processing"
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})
                    session['awaiting_image'] = False

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Customer harassment image handler failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs driver harassment with image
            elif (service == 'grab_cabs' and user_type == 'driver' and
                  session.get('sub_issue') == 'handle_passenger_harassment_complaint'):

                try:
                    from grab_cabs.driver.customer_experience import CustomerExperienceHandler
                    handler = CustomerExperienceHandler()

                    # Extract harassment type from session or messages
                    harassment_type = session.get('harassment_type')
                    if not harassment_type:
                        # Try to extract from conversation history
                        for msg in reversed(session.get('messages', [])):
                            if 'harassment report -' in msg.get('content', '').lower():
                                content = msg.get('content', '')
                                if 'Verbal Abuse' in content:
                                    harassment_type = 'Verbal Abuse'
                                elif 'Physical Abuse' in content:
                                    harassment_type = 'Physical Abuse'
                                elif 'Threats' in content:
                                    harassment_type = 'Threats'
                                elif 'Stalking' in content:
                                    harassment_type = 'Stalking'
                                elif 'Inappropriate Behaviour' in content:
                                    harassment_type = 'Inappropriate Behaviour'
                                break

                    response_text = handler.handle_passenger_harassment_complaint(
                        query=last_user_message,
                        harassment_type=harassment_type,
                        image_data=image_data,
                        workflow_stage="ai_processing"
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})
                    session['awaiting_image'] = False

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Driver harassment image handler failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs customer vehicle/ride issues with image
            elif (service == 'grab_cabs' and user_type == 'customer' and
                  session.get('sub_issue') in ['handle_unsafe_driving_behavior', 'handle_vehicle_problems', 'handle_accidents_during_ride']):

                try:
                    from grab_cabs.customer.driver_vehicle_issues import DriverVehicleIssuesHandler
                    handler = DriverVehicleIssuesHandler()

                    # Call the appropriate handler method
                    sub_issue = session.get('sub_issue')
                    if hasattr(handler, sub_issue):
                        method = getattr(handler, sub_issue)
                        response_text = method(query=last_user_message, image_data=image_data)
                    else:
                        # Fallback to generic processing
                        response_text = f"Thank you for reporting this {sub_issue.replace('_', ' ')} issue with image evidence. We are processing your complaint and will respond shortly."

                    session['messages'].append({'role': 'assistant', 'content': response_text})
                    session['awaiting_image'] = False

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Vehicle issues image handler failed: {e}")
                    # Fall through to AI engine processing

            # Special handling for grab_cabs customer other issues with image
            elif (service == 'grab_cabs' and user_type == 'customer' and
                  session.get('sub_issue') in ['handle_app_booking_issues', 'handle_cancellation_refund_policy_complications', 'handle_airport_booking_problems']):

                try:
                    # Use the enhanced AI engine directly for these issues
                    from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
                    ai_engine = EnhancedAgenticAIEngine()

                    response_text = ai_engine.process_complaint(
                        function_name=session.get('sub_issue'),
                        user_query=last_user_message,
                        service=service,
                        user_type=user_type,
                        image_data=image_data
                    )

                    session['messages'].append({'role': 'assistant', 'content': response_text})
                    session['awaiting_image'] = False

                    return jsonify({
                        'response': response_text,
                        'requires_image': False,
                        'conversation_id': conversation_id
                    })
                except Exception as e:
                    print(f"Other Grab Cabs issues image handler failed: {e}")
                    # Fall through to AI engine processing

            response_text = ai_engine.process_complaint(
                function_name=session['sub_issue'],
                user_query=last_user_message,
                service=service,
                user_type=user_type,
                image_data=image_data,
                username=session.get('username', 'anonymous'),
                order_id=session.get('order_id')
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
                    # Check method signature for supported parameters
                    import inspect
                    sig = inspect.signature(method)

                    # Build method call with available parameters
                    method_kwargs = {}
                    if 'image_data' in sig.parameters:
                        method_kwargs['image_data'] = image_data
                    if 'username' in sig.parameters:
                        method_kwargs['username'] = complaint_data.get('username', 'anonymous')
                    if 'order_id' in sig.parameters:
                        method_kwargs['order_id'] = complaint_data.get('order_id')

                    # Call method with appropriate parameters
                    if method_kwargs:
                        result = method(description, **method_kwargs)
                    else:
                        result = method(description)

                    print(f"AI Handler Result: {result[:200] if result else 'None'}...")
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
                    image_data=image_data,
                    username=complaint_data.get('username', 'anonymous'),
                    order_id=complaint_data.get('order_id')
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
            image_data=complaint_data.get('image_data'),
            username=complaint_data.get('username', 'anonymous'),
            order_id=complaint_data.get('order_id')
        )
        
        if final_result and len(final_result) > 100:
            print(f"Final AI result successful: {len(final_result)} chars")
            return final_result
    except Exception as e:
        print(f"Final AI call failed: {e}")
    
    # Absolute fallback
    print("Using absolute fallback response")
    return f"Thank you for your complaint. We have received your issue regarding {complaint_data['description'][:100]}... and our team is working on a resolution. You will receive an update within 24 hours."

@app.route('/api/order-update', methods=['POST'])
def create_order_update():
    """Create a cross-actor update for an order"""
    data = request.json

    required_fields = ['order_id', 'actor_type', 'actor_username', 'update_type', 'details']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    success = cross_actor_service.create_cross_actor_update(
        order_id=data['order_id'],
        actor_type=data['actor_type'],
        actor_username=data['actor_username'],
        update_type=data['update_type'],
        details=data['details']
    )

    if success:
        return jsonify({'success': True, 'message': 'Update created successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to create update (possibly blocked by spam prevention)'}), 400

@app.route('/api/notifications/<actor_type>/<username>', methods=['GET'])
def get_notifications(actor_type, username):
    """Get notifications for a specific actor"""
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'

    notifications = cross_actor_service.get_notifications_for_actor(
        actor_type=actor_type,
        username=username,
        unread_only=unread_only
    )

    return jsonify({'notifications': notifications})

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    success = cross_actor_service.mark_notification_as_read(notification_id)

    if success:
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    else:
        return jsonify({'success': False, 'message': 'Failed to mark notification as read'}), 400

@app.route('/api/order-history/<order_id>', methods=['GET'])
def get_order_history(order_id):
    """Get complete update timeline for an order"""
    timeline = cross_actor_service.get_order_update_timeline(order_id)

    return jsonify({'timeline': timeline})

@app.route('/api/orders/<user_type>/<username>/with-updates', methods=['GET'])
def get_orders_with_updates(user_type, username):
    """Get orders with update counts and recent notifications"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Get orders with update counts
        cursor.execute('''
            SELECT o.id, o.service, o.user_type, o.username, o.status, o.price,
                   o.start_latitude, o.start_longitude, o.start_address,
                   o.end_latitude, o.end_longitude, o.end_address,
                   o.customer_id, o.restaurant_id, o.driver_id, o.restaurant_name,
                   o.food_items, o.cab_type, o.products_ordered, o.payment_method,
                   o.date, o.details, o.update_count, o.current_status_remarks,
                   o.last_updated_by, o.last_update_timestamp,
                   COUNT(an.id) as unread_notifications
            FROM orders o
            LEFT JOIN actor_notifications an ON o.id = an.order_id
                AND an.target_actor_type = ? AND an.target_username = ? AND an.is_read = 0
            WHERE o.user_type = ? AND o.username = ?
            GROUP BY o.id
            ORDER BY o.date DESC
        ''', (user_type, username, user_type, username))

        orders = []
        for row in cursor.fetchall():
            orders.append({
                'id': row[0],
                'service': row[1],
                'user_type': row[2],
                'username': row[3],
                'status': row[4],
                'price': row[5],
                'start_latitude': row[6],
                'start_longitude': row[7],
                'start_address': row[8],
                'end_latitude': row[9],
                'end_longitude': row[10],
                'end_address': row[11],
                'customer_id': row[12],
                'restaurant_id': row[13],
                'driver_id': row[14],
                'restaurant_name': row[15],
                'food_items': row[16],
                'cab_type': row[17],
                'products_ordered': row[18],
                'payment_method': row[19],
                'date': row[20],
                'details': safe_json_loads(row[21]),
                'update_count': row[22] or 0,
                'current_status_remarks': row[23] or 'Order placed',
                'last_updated_by': row[24],
                'last_update_timestamp': row[25],
                'unread_notifications': row[26] or 0
            })

        return jsonify({'orders': orders})

    except Exception as e:
        print(f"Error fetching orders with updates: {e}")
        return jsonify({'error': 'Failed to fetch orders'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=8000)