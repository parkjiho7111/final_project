import sqlite3
import sys

def connect_db(db_file='being_test.db'):
    """Connect to the SQLite database"""
    return sqlite3.connect(db_file)

def show_stats(cursor):
    """Show database statistics"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    cursor.execute("SELECT COUNT(*) FROM being_test")
    total = cursor.fetchone()[0]
    print(f"Total records: {total}")
    
    cursor.execute("SELECT COUNT(DISTINCT genre) FROM being_test")
    genres = cursor.fetchone()[0]
    print(f"Unique genres: {genres}")
    
    cursor.execute("SELECT COUNT(DISTINCT region) FROM being_test")
    regions = cursor.fetchone()[0]
    print(f"Unique regions: {regions}")
    
    print("\n" + "-"*60)
    print("GENRES:")
    cursor.execute("SELECT genre, COUNT(*) as count FROM being_test GROUP BY genre ORDER BY count DESC")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} records")
    
    print("\n" + "-"*60)
    print("REGIONS:")
    cursor.execute("SELECT region, COUNT(*) as count FROM being_test GROUP BY region ORDER BY count DESC")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} records")
    print("="*60 + "\n")

def search_by_genre(cursor, genre):
    """Search policies by genre"""
    cursor.execute("SELECT id, title, region, period FROM being_test WHERE genre = ? LIMIT 10", (genre,))
    results = cursor.fetchall()
    
    if results:
        print(f"\nFound {len(results)} results for genre '{genre}' (showing first 10):")
        for row in results:
            print(f"\n  ID: {row[0]}")
            print(f"  Title: {row[1]}")
            print(f"  Region: {row[2]}")
            print(f"  Period: {row[3]}")
    else:
        print(f"\nNo results found for genre '{genre}'")

def search_by_region(cursor, region):
    """Search policies by region"""
    cursor.execute("SELECT id, title, genre, period FROM being_test WHERE region = ? LIMIT 10", (region,))
    results = cursor.fetchall()
    
    if results:
        print(f"\nFound {len(results)} results for region '{region}' (showing first 10):")
        for row in results:
            print(f"\n  ID: {row[0]}")
            print(f"  Title: {row[1]}")
            print(f"  Genre: {row[2]}")
            print(f"  Period: {row[3]}")
    else:
        print(f"\nNo results found for region '{region}'")

def search_by_keyword(cursor, keyword):
    """Search policies by keyword in title or summary"""
    cursor.execute("""
        SELECT id, title, genre, region, period 
        FROM being_test 
        WHERE title LIKE ? OR summary LIKE ? 
        LIMIT 10
    """, (f'%{keyword}%', f'%{keyword}%'))
    results = cursor.fetchall()
    
    if results:
        print(f"\nFound {len(results)} results for keyword '{keyword}' (showing first 10):")
        for row in results:
            print(f"\n  ID: {row[0]}")
            print(f"  Title: {row[1]}")
            print(f"  Genre: {row[2]}")
            print(f"  Region: {row[3]}")
            print(f"  Period: {row[4]}")
    else:
        print(f"\nNo results found for keyword '{keyword}'")

def get_policy_detail(cursor, policy_id):
    """Get detailed information about a specific policy"""
    cursor.execute("SELECT * FROM being_test WHERE id = ?", (policy_id,))
    result = cursor.fetchone()
    
    if result:
        print("\n" + "="*60)
        print("POLICY DETAILS")
        print("="*60)
        print(f"ID: {result[0]}")
        print(f"Title: {result[1]}")
        print(f"Summary: {result[2]}")
        print(f"Period: {result[3]}")
        print(f"Link: {result[4]}")
        print(f"Genre: {result[5]}")
        print(f"Region: {result[6]}")
        print(f"Original ID: {result[7]}")
        print(f"Created At: {result[8]}")
        print(f"Updated At: {result[9]}")
        print("="*60 + "\n")
    else:
        print(f"\nNo policy found with ID {policy_id}")

def main():
    conn = connect_db()
    cursor = conn.cursor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 query_db.py stats                    - Show database statistics")
        print("  python3 query_db.py genre <genre_name>       - Search by genre")
        print("  python3 query_db.py region <region_name>     - Search by region")
        print("  python3 query_db.py keyword <keyword>        - Search by keyword")
        print("  python3 query_db.py detail <id>              - Get policy details")
        print("\nExamples:")
        print("  python3 query_db.py stats")
        print("  python3 query_db.py genre 취업/직무")
        print("  python3 query_db.py region 충남")
        print("  python3 query_db.py keyword 청년")
        print("  python3 query_db.py detail 1")
        conn.close()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'stats':
        show_stats(cursor)
    elif command == 'genre' and len(sys.argv) > 2:
        search_by_genre(cursor, sys.argv[2])
    elif command == 'region' and len(sys.argv) > 2:
        search_by_region(cursor, sys.argv[2])
    elif command == 'keyword' and len(sys.argv) > 2:
        search_by_keyword(cursor, sys.argv[2])
    elif command == 'detail' and len(sys.argv) > 2:
        get_policy_detail(cursor, int(sys.argv[2]))
    else:
        print("Invalid command or missing arguments")
    
    conn.close()

if __name__ == "__main__":
    main()
