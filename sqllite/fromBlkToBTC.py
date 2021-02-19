import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

dirGraph = nx.DiGraph() # 방향 그래프

print("탐색을 위한 index의 범위를 입력해주세요. (총 개수, OFFSET)")
print("EX) [Input] 10 30 -> [Output] 31행 ~ 40행까지의 그래프")

cnt, offset = map(int, input().split())

####################################################################################################################
# 1.

conn = sqlite3.connect("dbv3-core.db") # dbv3-core.db.와 연결
cur = conn.cursor() # 커서 생성
cur.execute("SELECT * FROM BlkTx LIMIT %d OFFSET %d" %(cnt, offset)) # SELECT 쿼리문 실행
blkTxInfo = cur.fetchall() # 결과를 clusterInfo에 저장, clusterInfo에는 addr과 cluster의 인덱스 관계가 저장.

# 특정 클러스터와 이와 관련된 addr이 dict형 변수에 저장.
# node_blkTx[cluster number] = [cluster number, [addr]]
visit = {}
node_blkTx = {}

for row in blkTxInfo:
    visit[row[0]] = False

for row in blkTxInfo:
    if visit[row[0]] == False: 
        node_blkTx[row[0]] = [row[0], []]
        visit[row[0]] = True 
    node_blkTx[row[0]][1].append(row[1])

####################################################################################################################
# 2.

cur.execute("SELECT * FROM TxOut LIMIT %d OFFSET %d" %(cnt, offset)) # SELECT 쿼리문 실행
txOutInfo = cur.fetchall() # 결과를 txOutInfo에 저장, clusterInfo에는 tx와 addr, btc 관계가 저장.

# 특정 tk와 이와 관련된 addr, btc, 거래 개수가 dict형 변수에 저장.
# node_txOut[tk number] = [tk number, [addr, btc], 거래 개수]
visit = {}
node_txOut = {}

for row in txOutInfo:
    visit[row[0]] = False

for row in txOutInfo:
    if visit[row[0]] == False: 
        node_txOut[row[0]] = [row[0], [], 0] # cluster 별로 cluster와 addr 저장.
        visit[row[0]] = True 
    node_txOut[row[0]][1].append([row[2], row[3]]) # tx 저장.
    node_txOut[row[0]][2] = row[1] + 1 # tx의 addr 개수 저장

####################################################################################################################
# 3. 1, 2가 종료되면 node_blkTx에는  block과 transaction의 관계, node_txOut에는 transaction과 addr, btc, 거래 개수 관계가 저장.

print("")
print("출력하고자 하는 그래프의 범위를 입력해주세요. (1. Block / 2.Transaction / 3.Addr / 4.BTC)")
print("EX) [Input] 1 4 -> [Output] Block - Transaction - Addr - BTC 모두 출력하는 그래프")
print("EX) [Input] 3 4 -> [Output] Addr - BTC 출력하는 그래프")

####################################################################################################################
# 4. 입력한 범위에 따라 그래프 생성

a, b = map(int, input().split())

for i in range(a, b):
    if i == 1:
        curNode = "Block "
        nextNode = "Transaction "
    elif i == 2:
        curNode = "Transaction "
        nextNode = "Addr "
    else:
        curNode = "Addr "
        nextNode = " BTC"
    
    # 아래 코드는 Block - Transaction 그래프를 출력하기 위한 코드이지만 지금처럼 index를 입력받은 경우에 dbv3.service.db, dbv3.core.db에서 해당 index의 결과가 달라서
    # 내가 원하는 모양인 Block - Transaction - Addr - BTC를 출력할 수 없다.
    ''' 
    if i == 1:
        for element in node_blkTx:
            for addr in node_blkTx[element][1]:
                dirGraph.add_edge(curNode + str(element), nextNode + str(addr))
    '''

    if i == 2: # Transaction - Addr
        for element in node_txOut:
            for addr in node_txOut[element][1]:
                dirGraph.add_edge(curNode + str(element), nextNode + str(addr[0]))

    elif i == 3: # Addr - BTC
        for element in node_txOut:
            for addr in node_txOut[element][1]:
                dirGraph.add_edge(curNode + str(addr[0]), str(addr[1]) + nextNode)
    
# 라벨 표시안하려면 with_labels 파라미터 지우거나 False
nx.draw(dirGraph, with_labels=True)

# 이 py 파일 위치하는 곳에 사진으로 저장
plt.savefig("fromBlkToBTC_dirGraph.png")

plt.show()