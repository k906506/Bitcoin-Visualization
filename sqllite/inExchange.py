import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

dirGraph = nx.DiGraph() # 방향 그래프
node = {}

def returnTagId(tagId):
    if tagId == "업비트":
        return 942
    elif tagId == "빗썸":
        return 167
    elif tagId == "코인원":
        return 390
    else:
        return -1
    
print("거래소의 거래 과정을 보여줍니다.")
print("거래소를 입력해주세요. Ex) 업비트, 빗썸, 코인원")
inputExchange = input()

print("")
print("해당 거래소로 INPUT된 거래를 확인하시려면 1번, OUTPUT된 거래는 확인하시려면 2번을 눌러주세요.")
showOutputType = int(input())

print("")
print("출력할 그래프의 최대 개수를 입력해주세요.")
cnt = int(input())

###################################################################################################################
# 1.

node[inputExchange] = []
exchangeTagId = returnTagId(inputExchange)

conn = sqlite3.connect("dbv3-service.db")
cur = conn.cursor()

cur.execute("SELECT * FROM Tag where tag = %d LIMIT %d" %(exchangeTagId, cnt))
exchangeAddrInfo = cur.fetchall()
node[inputExchange] = exchangeAddrInfo

###################################################################################################################
# 2.

conn = sqlite3.connect("dbv3-core.db")
cur = conn.cursor()

node_element = []
for element in node[inputExchange]:
    node_element.append(element[0])

if showOutputType == 1: # INPUT된 거래
    for element in node[inputExchange]:
        cur.execute("SELECT * FROM TxOut where addr = %d LIMIT %d" %(element[0], cnt))
        txOutInfo = cur.fetchall()
        for row in txOutInfo:
            dirGraph.add_edge(row[0], row[2], weight = row[3])

elif showOutputType == 2: # OUTPUT된 거래
    for element in node[inputExchange]:
        cur.execute("SELECT * FROM TxOut where tx = %d LIMIT %d" %(element[0], cnt))
        txOutInfo = cur.fetchall()
        for row in txOutInfo:
            dirGraph.add_edge(row[0], row[2], weight = row[3])

else: # 오류
    pass

###################################################################################################################
# 3.

pos = nx.spring_layout(dirGraph)
nx.draw(dirGraph, pos = pos, with_labels = True)
labels = nx.get_edge_attributes(dirGraph, 'weight')
nx.draw_networkx_edge_labels(dirGraph, pos, edge_labels = labels)

nx.draw_networkx_nodes(dirGraph, pos, nodelist = node_element, node_color= '#FF1744')

# 사진으로 저장
plt.savefig("inExchange_DirGraph.png")

plt.show()