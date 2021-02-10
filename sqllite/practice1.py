import sqlite3

conn = sqlite3.connect("dbv-service.db") # dbv3-service.db.와 연결

cur = conn.cursor() # 커서 생성
 
cur.execute("SELECT * FROM STUDENT") # SELECT 쿼리문 실행

rows = cur.fetchall() # 결과를 rows에 저장
for row in rows:
    print("학번 : %s, 이름 : %s, 나이 : %d" %(row[0], row[1], row[2]))

conn.close() # 연결 해제