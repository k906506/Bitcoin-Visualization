import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

dirGraph = nx.DiGraph() # 무방향

conn = sqlite3.connect("dbv-service.db") # dbv3-service.db.와 연결

cur = conn.cursor() # 커서 생성
 
cur.execute("SELECT * FROM STUDENT") # SELECT 쿼리문 실행

rows = cur.fetchall() # 결과를 rows에 저장
for row in rows:
    name = row[0]
    subject = row[1]
    score = row[2]
    dirGraph.add_nodes_from(row)
    dirGraph.add_edge(row[0], row[1])
    dirGraph.add_edge(row[1], row[2])

conn.close() # 연결 해제

nx.draw(dirGraph, with_labels=True)

# 이 py 파일 위치하는 곳에 사진으로 저장
plt.savefig("practice1.png")

plt.show()