import json
import sqlite3
from pathlib import Path

def create_table(cursor):
    """Create being_test table"""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS being_test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        summary TEXT,
        period TEXT,
        link TEXT,
        genre TEXT,
        region TEXT,
        original_id TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_genre ON being_test(genre)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON being_test(region)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_original_id ON being_test(original_id)")
    
    print("Table 'being_test' created successfully")

def insert_policy_data(cursor, policy):
    """Insert a single policy record into the database"""
    query = """
    INSERT OR REPLACE INTO being_test (title, summary, period, link, genre, region, original_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
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
        return True
    except Exception as e:
        print(f"Error inserting policy {policy.get('original_id', 'unknown')}: {e}")
        return False

def main():
    # Database file path
    db_file = 'being_test.db'
    
    # Read JSON file
    print("Reading policies_remake.json...")
    json_file = Path(__file__).parent / 'policies_remake.json'
    
    with open(json_file, 'r', encoding='utf-8') as f:
        policies = json.load(f)
    
    print(f"Found {len(policies)} policies to insert")
    
    # Create database connection
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create table
    create_table(cursor)
    
    # Insert policies
    success_count = 0
    fail_count = 0
    
    for i, policy in enumerate(policies, 1):
        if insert_policy_data(cursor, policy):
            success_count += 1
        else:
            fail_count += 1
        
        # Print progress every 100 records
        if i % 100 == 0:
            print(f"Processed {i}/{len(policies)} policies...")
    
    # Commit changes
    conn.commit()
    
    # Print statistics
    cursor.execute("SELECT COUNT(*) FROM being_test")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT genre) FROM being_test")
    total_genres = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT region) FROM being_test")
    total_regions = cursor.fetchone()[0]
    
    print(f"\n{'='*50}")
    print(f"Import completed!")
    print(f"{'='*50}")
    print(f"Successfully inserted: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total records in database: {total_records}")
    print(f"Total unique genres: {total_genres}")
    print(f"Total unique regions: {total_regions}")
    print(f"\nDatabase file created: {db_file}")
    print(f"{'='*50}")
    
    # Show sample data
    print("\nSample data (first 5 records):")
    cursor.execute("SELECT id, title, genre, region FROM being_test LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Title: {row[1][:50]}..., Genre: {row[2]}, Region: {row[3]}")
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    main()
