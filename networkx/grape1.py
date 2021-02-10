import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

# 노드 = 원, 엣지 = 선 (add_node를 안하고 add_edge(1,2)을 해도 노드 1, 2는 자동 생성됨
G.add_nodes_from([1, 2, 3, 4])
G.add_edges_from([(1, 2), (2, 1), (2, 3), (2,4)])

# 라벨 표시안하려면 with_labels 파라미터 지우거나 False
nx.draw(G, with_labels=True)

# 이 py 파일 위치하는 곳에 사진으로 저장
plt.savefig("G.png")

plt.show()
