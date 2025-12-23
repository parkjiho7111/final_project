import json
import mysql.connector
from mysql.connector import Error

def create_connection(host='localhost', user='root', password='', database=''):
    """Create a database connection"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def insert_policy_data(connection, policy):
    """Insert a single policy record into the database"""
    cursor = connection.cursor()
    query = """
    INSERT INTO being_test (title, summary, period, link, genre, region, original_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        summary = VALUES(summary),
        period = VALUES(period),
        link = VALUES(link),
        genre = VALUES(genre),
        region = VALUES(region)
    """
    
    values = (
        policy.get('title', ''),
        policy.get('summary', ''),
        policy.get('period', ''),
        policy.get('link', ''),
        policy.get('genre', ''),
        policy.get('region', ''),
        policy.get('original_id', '')
    )
    
    try:
        cursor.execute(query, values)
        connection.commit()
        return True
    except Error as e:
        print(f"Error inserting policy {policy.get('original_id', 'unknown')}: {e}")
        return False

def main():
    # Database configuration - Update these values as needed
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''  # Update with your password
    DB_NAME = 'your_database_name'  # Update with your database name
    
    # Read JSON file
    print("Reading policies_remake.json...")
    with open('policies_remake.json', 'r', encoding='utf-8') as f:
        policies = json.load(f)
    
    print(f"Found {len(policies)} policies to insert")
    
    # Create database connection
    connection = create_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    
    if connection is None:
        print("Failed to connect to database")
        return
    
    # Insert policies
    success_count = 0
    fail_count = 0
    
    for i, policy in enumerate(policies, 1):
        if insert_policy_data(connection, policy):
            success_count += 1
        else:
            fail_count += 1
        
        # Print progress every 100 records
        if i % 100 == 0:
            print(f"Processed {i}/{len(policies)} policies...")
    
    print(f"\nImport completed!")
    print(f"Successfully inserted: {success_count}")
    print(f"Failed: {fail_count}")
    
    # Close connection
    connection.close()

if __name__ == "__main__":
    main()
