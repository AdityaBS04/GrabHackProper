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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            user_type TEXT NOT NULL,
            username TEXT NOT NULL,
            status TEXT NOT NULL,
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
    
    # Insert demo users
    demo_users = [
        ('customer1', 'pass123', 'customer'),
        ('agent1', 'pass123', 'delivery_agent'),
        ('resto1', 'pass123', 'restaurant'),
        ('driver1', 'pass123', 'driver'),
        ('store1', 'pass123', 'darkstore')
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO users (username, password, user_type) VALUES (?, ?, ?)',
        demo_users
    )
    
    # Insert demo orders
    demo_orders = [
        ('GF001', 'grab_food', 'customer', 'customer1', 'completed', '2024-09-01', '{"restaurant": "Pizza Palace", "total": 25.50}'),
        ('GF002', 'grab_food', 'customer', 'customer1', 'in_progress', '2024-09-06', '{"restaurant": "Burger Joint", "total": 18.75}'),
        ('GC001', 'grab_cabs', 'customer', 'customer1', 'completed', '2024-09-02', '{"from": "Downtown", "to": "Airport", "total": 15.00}'),
        ('GM001', 'grab_mart', 'customer', 'customer1', 'completed', '2024-09-03', '{"store": "FreshMart", "items": 12, "total": 45.80}'),
        ('GF003', 'grab_food', 'delivery_agent', 'agent1', 'assigned', '2024-09-06', '{"order_id": "GF002", "pickup": "Burger Joint"}'),
        ('GF004', 'grab_food', 'restaurant', 'resto1', 'preparing', '2024-09-06', '{"order_id": "GF002", "items": 3}'),
        ('GC002', 'grab_cabs', 'driver', 'driver1', 'active', '2024-09-06', '{"passenger": "John Doe", "pickup": "Mall"}'),
        ('GM002', 'grab_mart', 'darkstore', 'store1', 'picking', '2024-09-06', '{"order_id": "GM002", "items": 8}')
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO orders (id, service, user_type, username, status, date, details) VALUES (?, ?, ?, ?, ?, ?, ?)',
        demo_orders
    )
    
    conn.commit()
    conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM users WHERE username = ? AND password = ? AND user_type = ?',
        (username, password, user_type)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/orders/<user_type>/<username>', methods=['GET'])
def get_orders(user_type, username):
    """Get orders for a specific user"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM orders WHERE user_type = ? AND username = ? ORDER BY date DESC',
        (user_type, username)
    )
    
    orders = []
    for row in cursor.fetchall():
        orders.append({
            'id': row[0],
            'service': row[1],
            'user_type': row[2],
            'username': row[3],
            'status': row[4],
            'date': row[5],
            'details': json.loads(row[6] or '{}')
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
                {'id': 'performance_handler', 'name': 'Performance Support'}
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
        
        # Find matching sub-issues for the category (category_id is actually handler name)
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
        
        # If we have both category and sub_issue, use conversational AI processing
        if category and sub_issue:
            from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
            ai_engine = EnhancedAgenticAIEngine()
            
            # Build conversation context from previous messages
            conversation_context = ""
            for msg in session['messages']:
                role = "Customer" if msg['role'] == 'user' else "Agent"
                conversation_context += f"{role}: {msg['content']}\n"
            
            # Use conversational processing
            response = ai_engine.process_conversation(
                message=message,
                service=service,
                user_type=user_type,
                conversation_history=session['messages'],
                session_context={
                    'category': category,
                    'sub_issue': sub_issue,
                    'conversation_context': conversation_context,
                    'username': username
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
                session_context=session['context']
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