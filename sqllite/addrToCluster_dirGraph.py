import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

dirGraph = nx.DiGraph() # 방향 그래프

print("탐색을 위한 index의 범위를 입력해주세요. (총 개수, OFFSET)")
print("[Input] 10 30 -> [Output] 31행 ~ 40행까지의 그래프")

cnt, offset = map(int, input().split())

conn = sqlite3.connect("dbv3-service.db") # dbv3-core.db.와 연결
cur = conn.cursor() # 커서 생성
cur.execute("SELECT * FROM Cluster LIMIT %d OFFSET %d" %(cnt, offset)) # SELECT 쿼리문 실행
clusterInfo = cur.fetchall() # 결과를 clusterInfo에 저장, clusterInfo에는 addr과 cluster의 인덱스 관계가 저장.

# 특정 클러스터와 이와 관련된 addr이 dict형 변수에 저장.
# node[cluster number] = [cluster number, [addr]]

visit = {}
node = {}

for row in clusterInfo:
    visit[row[1]] = False

for row in clusterInfo:
    if visit[row[1]] == False: 
        node[row[1]] = [row[1], []] # cluster 별로 cluster와 addr 저장.
        visit[row[1]] = True 
    node[row[1]][1].append(row[0]) # addr 저장.

# addr -> cluster 방향성을 지닌 그래프 생성
for element in node:
    for addr in node[element][1]:
        dirGraph.add_edge("Addr " + str(addr), "Cluster " + str(node[element][0]))
    
# 라벨 표시안하려면 with_labels 파라미터 지우거나 False
nx.draw(dirGraph, with_labels=True)

# 이 py 파일 위치하는 곳에 사진으로 저장
plt.savefig("addrToCluster_dirGraph.png")

plt.show()