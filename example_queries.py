"""
간단한 데이터베이스 사용 예제
Example usage of the being_test database
"""

import sqlite3

def example_1_basic_query():
    """예제 1: 기본 쿼리"""
    print("\n" + "="*60)
    print("예제 1: 충남 지역의 취업 관련 정책 조회")
    print("="*60)
    
    conn = sqlite3.connect('being_test.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, summary, period 
        FROM being_test 
        WHERE region = '충남' AND genre = '취업/직무'
        LIMIT 5
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n{i}. {row[0]}")
        print(f"   요약: {row[1][:100]}...")
        print(f"   기간: {row[2]}")
    
    conn.close()

def example_2_count_by_genre():
    """예제 2: 장르별 개수 세기"""
    print("\n" + "="*60)
    print("예제 2: 장르별 정책 개수")
    print("="*60)
    
    conn = sqlite3.connect('being_test.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT genre, COUNT(*) as count 
        FROM being_test 
        GROUP BY genre 
        ORDER BY count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]}개")
    
    conn.close()

def example_3_search_keyword():
    """예제 3: 키워드 검색"""
    print("\n" + "="*60)
    print("예제 3: '창업' 키워드 검색")
    print("="*60)
    
    conn = sqlite3.connect('being_test.db')
    cursor = conn.cursor()
    
    keyword = '창업'
    cursor.execute("""
        SELECT title, genre, region 
        FROM being_test 
        WHERE title LIKE ? OR summary LIKE ?
        LIMIT 10
    """, (f'%{keyword}%', f'%{keyword}%'))
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n{i}. {row[0]}")
        print(f"   장르: {row[1]}, 지역: {row[2]}")
    
    conn.close()

def example_4_complex_query():
    """예제 4: 복잡한 쿼리 - 지역별, 장르별 집계"""
    print("\n" + "="*60)
    print("예제 4: 지역별 취업 관련 정책 개수 (상위 5개 지역)")
    print("="*60)
    
    conn = sqlite3.connect('being_test.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT region, COUNT(*) as count 
        FROM being_test 
        WHERE genre = '취업/직무'
        GROUP BY region 
        ORDER BY count DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]}개")
    
    conn.close()

def example_5_get_policy_details():
    """예제 5: 특정 정책의 상세 정보"""
    print("\n" + "="*60)
    print("예제 5: ID 1번 정책의 상세 정보")
    print("="*60)
    
    conn = sqlite3.connect('being_test.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM being_test WHERE id = 1")
    row = cursor.fetchone()
    
    if row:
        print(f"\nID: {row[0]}")
        print(f"제목: {row[1]}")
        print(f"요약: {row[2]}")
        print(f"기간: {row[3]}")
        print(f"링크: {row[4]}")
        print(f"장르: {row[5]}")
        print(f"지역: {row[6]}")
        print(f"원본 ID: {row[7]}")
    
    conn.close()

def example_6_recent_policies():
    """예제 6: 2025년 정책 찾기"""
    print("\n" + "="*60)
    print("예제 6: 2025년 진행 중인 정책 (샘플 10개)")
    print("="*60)
    
    conn = sqlite3.connect('being_test.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, period, region, genre 
        FROM being_test 
        WHERE period LIKE '%2025%'
        LIMIT 10
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n{i}. {row[0]}")
        print(f"   기간: {row[1]}")
        print(f"   지역: {row[2]}, 장르: {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    print("\n" + "🔍 Being Test Database - 사용 예제")
    print("="*60)
    
    # 모든 예제 실행
    example_1_basic_query()
    example_2_count_by_genre()
    example_3_search_keyword()
    example_4_complex_query()
    example_5_get_policy_details()
    example_6_recent_policies()
    
    print("\n" + "="*60)
    print("✅ 모든 예제 실행 완료!")
    print("="*60 + "\n")
