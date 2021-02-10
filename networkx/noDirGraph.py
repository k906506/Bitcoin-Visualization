import networkx as nx
import matplotlib.pyplot as plt

noDirGraph = nx.Graph() # 무방향

n, m = map(int, input().split()) # 노드 개수, 엣지 개수 입력

node = list(input().split())    # 노드 정보 입력

for i in range(n): # 그래프에 노드 추가
    noDirGraph.add_node(node[i])

for i in range(m): # 그래프에 출발 노드, 도착 노드 입력
    start, end = input().split()
    noDirGraph.add_edge(start, end)

"""
input example
7 8
A B C D E F G
A B
A C
A D
B D
B E
E F
F G
G A
"""
    
# 라벨 표시안하려면 with_labels 파라미터 지우거나 False
nx.draw(noDirGraph, with_labels=True)

# 이 py 파일 위치하는 곳에 사진으로 저장
plt.savefig("noDirGraph.png")

plt.show()