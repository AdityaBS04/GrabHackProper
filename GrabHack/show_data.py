#!/usr/bin/env python3
"""
Display comprehensive database data in a nice format
"""

import sqlite3
import json

def show_data():
    conn = sqlite3.connect('grabhack.db')
    cursor = conn.cursor()

    print('=== GRAB FOOD CUSTOMER ORDERS ===')
    cursor.execute('SELECT id, username, status, price, payment_method, restaurant_name, food_items FROM orders WHERE service="grab_food" AND user_type="customer" ORDER BY username, date')
    orders = cursor.fetchall()

    current_user = None
    for order_id, username, status, price, payment, restaurant, food_items in orders:
        if username != current_user:
            if current_user is not None:
                print()
            print(f'CUSTOMER: {username.upper()}')
            current_user = username
        
        food_short = food_items[:40] + '...' if food_items and len(food_items) > 40 else food_items or 'N/A'
        price_str = f'${price:.2f}' if price else '$0.00'
        print(f'  {order_id}: {restaurant} | {status} | {price_str} ({payment}) | {food_short}')

    print('\n=== DELIVERY AGENT ACTIVITIES ===')
    cursor.execute('SELECT id, username, status, restaurant_name, details FROM orders WHERE user_type="delivery_agent" ORDER BY username')
    agent_orders = cursor.fetchall()

    current_agent = None
    for order_id, username, status, restaurant, details in agent_orders:
        if username != current_agent:
            if current_agent is not None:
                print()
            print(f'AGENT: {username.upper()}')
            current_agent = username
        
        details_obj = json.loads(details) if details else {}
        handling = details_obj.get('assigned_order', details_obj.get('order_id', 'N/A'))
        print(f'  {order_id}: {status} at {restaurant} | Handling order: {handling}')

    print('\n=== RESTAURANT STATUS ===')
    cursor.execute('SELECT id, username, status, restaurant_name, details FROM orders WHERE user_type="restaurant" ORDER BY username')
    resto_orders = cursor.fetchall()

    current_resto = None
    for order_id, username, status, restaurant, details in resto_orders:
        if username != current_resto:
            if current_resto is not None:
                print()
            print(f'RESTAURANT: {username.upper()}')
            current_resto = username
        
        details_obj = json.loads(details) if details else {}
        prep_order = details_obj.get('preparing_order', details_obj.get('ready_order', details_obj.get('delayed_order', 'N/A')))
        delay = details_obj.get('estimated_delay_minutes', details_obj.get('prep_time_minutes'))
        delay_info = f' (ETA: {delay} min)' if delay else ''
        print(f'  {order_id}: {status} | Working on: {prep_order}{delay_info}')

    print('\n=== CREDIBILITY SCORES & STATS ===')
    cursor.execute('SELECT username, credibility_score FROM users WHERE user_type="customer" ORDER BY credibility_score DESC')
    customers = cursor.fetchall()

    for username, score in customers:
        # Get order stats
        cursor.execute('SELECT COUNT(*), COUNT(CASE WHEN status="completed" THEN 1 END), AVG(price) FROM orders WHERE username = ? AND service="grab_food" AND user_type="customer"', (username,))
        total, completed, avg_price = cursor.fetchone()
        
        # Get complaint count (unique)
        cursor.execute('SELECT COUNT(DISTINCT category) FROM complaints WHERE username = ?', (username,))
        complaints = cursor.fetchone()[0]
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        avg_price_str = f'${avg_price:.2f}' if avg_price else '$0.00'
        
        print(f'  {username}: Score {score}/10 | {total} orders ({completion_rate:.0f}% completed) | Avg: {avg_price_str} | {complaints} complaints')

    print('\n=== RECENT COMPLAINTS ===')
    cursor.execute('SELECT DISTINCT username, user_type, category, description FROM complaints ORDER BY category')
    complaints = cursor.fetchall()

    for username, user_type, category, description in complaints:
        desc_short = description[:60] + '...' if len(description) > 60 else description
        print(f'  {username} ({user_type}): {category} - {desc_short}')

    conn.close()

if __name__ == "__main__":
    show_data()