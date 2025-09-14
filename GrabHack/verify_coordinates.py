#!/usr/bin/env python3
"""
Verify all database entries have been converted to coordinate format correctly
"""

import sqlite3
import os

DATABASE_PATH = 'grabhack.db'

def verify_coordinate_database():
    """Verify all orders in the database have coordinate data"""

    if not os.path.exists(DATABASE_PATH):
        print("ERROR: Database not found. Please run the app to initialize it.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check all orders have coordinate data
    cursor.execute('''
        SELECT COUNT(*) as total_orders,
               COUNT(CASE WHEN start_latitude IS NOT NULL AND start_longitude IS NOT NULL THEN 1 END) as with_start_coords,
               COUNT(CASE WHEN end_latitude IS NOT NULL AND end_longitude IS NOT NULL THEN 1 END) as with_end_coords,
               COUNT(CASE WHEN start_address IS NOT NULL THEN 1 END) as with_start_address,
               COUNT(CASE WHEN end_address IS NOT NULL THEN 1 END) as with_end_address
        FROM orders
    ''')

    stats = cursor.fetchone()
    total, start_coords, end_coords, start_addr, end_addr = stats

    print("=== COORDINATE DATABASE VERIFICATION ===")
    print(f"Total Orders: {total}")
    print(f"Orders with Start Coordinates: {start_coords}/{total} ({100*start_coords/total:.1f}%)")
    print(f"Orders with End Coordinates: {end_coords}/{total} ({100*end_coords/total:.1f}%)")
    print(f"Orders with Start Address: {start_addr}/{total} ({100*start_addr/total:.1f}%)")
    print(f"Orders with End Address: {end_addr}/{total} ({100*end_addr/total:.1f}%)")

    # Check for any orders missing coordinate data
    cursor.execute('''
        SELECT id, service, user_type, start_latitude, start_longitude, end_latitude, end_longitude
        FROM orders
        WHERE start_latitude IS NULL OR start_longitude IS NULL
           OR end_latitude IS NULL OR end_longitude IS NULL
        LIMIT 5
    ''')

    missing_coords = cursor.fetchall()
    if missing_coords:
        print(f"\nWARNING: {len(missing_coords)} orders found with missing coordinates:")
        for order in missing_coords:
            order_id, service, user_type, start_lat, start_lng, end_lat, end_lng = order
            print(f"  - {order_id} ({service}/{user_type}): start=({start_lat},{start_lng}), end=({end_lat},{end_lng})")
    else:
        print(f"\nSUCCESS: All {total} orders have complete coordinate data!")

    # Test sample coordinates for different services
    cursor.execute('''
        SELECT id, service, user_type, start_latitude, start_longitude, start_address,
               end_latitude, end_longitude, end_address, cab_type
        FROM orders
        WHERE service IN ('grab_cabs', 'grab_food', 'grab_express', 'grab_mart')
        ORDER BY service, date DESC
        LIMIT 2
    ''')

    print(f"\n=== SAMPLE COORDINATE DATA BY SERVICE ===")
    sample_orders = cursor.fetchall()

    for order in sample_orders:
        order_id, service, user_type, start_lat, start_lng, start_addr, end_lat, end_lng, end_addr, cab_type = order

        print(f"\n{service.upper()} Order: {order_id} ({user_type})")
        print(f"  From: {start_addr} ({start_lat:.4f}, {start_lng:.4f})")
        print(f"  To: {end_addr} ({end_lat:.4f}, {end_lng:.4f})")

        if service == 'grab_cabs':
            # Generate Google Maps URL for verification
            maps_url = f"https://www.google.com/maps/dir/{start_lat},{start_lng}/{end_lat},{end_lng}/"
            print(f"  Google Maps: {maps_url}")

    # Test Bangalore coordinate ranges (approximately)
    cursor.execute('''
        SELECT COUNT(*) as bangalore_orders
        FROM orders
        WHERE start_latitude BETWEEN 12.8 AND 13.2
          AND start_longitude BETWEEN 77.4 AND 77.8
          AND end_latitude BETWEEN 12.8 AND 13.2
          AND end_longitude BETWEEN 77.4 AND 77.8
    ''')

    bangalore_count = cursor.fetchone()[0]
    print(f"\n=== LOCATION VERIFICATION ===")
    print(f"Orders within Bangalore region: {bangalore_count}/{total} ({100*bangalore_count/total:.1f}%)")

    # Show coordinate distribution by area
    cursor.execute('''
        SELECT
            CASE
                WHEN start_address LIKE '%Koramangala%' THEN 'Koramangala'
                WHEN start_address LIKE '%Jayanagar%' THEN 'Jayanagar'
                WHEN start_address LIKE '%Whitefield%' THEN 'Whitefield'
                WHEN start_address LIKE '%Banashankari%' THEN 'Banashankari'
                WHEN start_address LIKE '%MG Road%' OR start_address LIKE '%Brigade%' THEN 'Central Bangalore'
                ELSE 'Other Areas'
            END as area,
            COUNT(*) as order_count
        FROM orders
        GROUP BY area
        ORDER BY order_count DESC
    ''')

    print(f"\n=== ORDER DISTRIBUTION BY AREA ===")
    areas = cursor.fetchall()
    for area, count in areas:
        print(f"  {area}: {count} orders")

    conn.close()

    if start_coords == total and end_coords == total:
        print(f"\nCOMPLETE SUCCESS! All {total} orders now have precise coordinate data for Google Maps integration!")
        return True
    else:
        print(f"\nINCOMPLETE: {total - min(start_coords, end_coords)} orders still need coordinate updates.")
        return False

if __name__ == "__main__":
    verify_coordinate_database()