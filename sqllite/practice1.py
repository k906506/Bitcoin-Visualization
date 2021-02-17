import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

dirGraph = nx.Graph() # 무방향

conn = sqlite3.connect("dbv3-core.db") # dbv3-core.db.와 연결
cur = conn.cursor() # 커서 생성

cur.execute("SELECT * FROM BlkTx") # SELECT 쿼리문 실행
blkToTx = cur.fetchall() # 결과를 blkToTx에 저장, blkToTx에는 blk와 tx 인덱스 관계가 저장.

cur.execute("SELECT * FROM txIn") # SELECT 쿼리문 실행
txInInfo = cur.fetchall() # 결과를 txInInfo에 저장, txInInfo에는 tx, n, ptx, pn 순으로 저장.

cur.execute("SELECT * FROM txOut") # SELECT 쿼리문 실행
txOutInfo = cur.fetchall() # 결과를 txOutInfo에 저장, txOutInfo에는 tx, n, addr, btc 순으로 저장.

index_info = {} # blk와 tx 인덱스 관계, address index, input, output을 저장할 dict형 변수

for row in blkToTx:
    index_info[row[0]] = [0, 0, 0, 0] # tx 인덱스, address 인덱스, input, output
    index_info[row[0]][0] = row[1] # tx 인덱스 정보 저장

index = 0
for row in txOutInfo:
    index_info[index][1] = row[2] # row[2]는 address 인덱스
    index_info[index][3] = row[3] # row[3]은 output
    index += 1

############################################################################################

hash_info = {} # index_info에 들어있는 index의 실제 해시

conn = sqlite3.connect("dbv3-index.db") # dbv3-index.db.와 연결
cur = conn.cursor() # 커서 생성

cur.execute("SELECT * FROM BlkID") # SELECT 쿼리문 실행
blkIdInfo = cur.fetchall() # 결과를 blkIdInfo에 저장, blkIdInfo에는 index와 실제 blk 해시 주소가 저장

cur.execute("SELECT * FROM AddrId") # SELECT 쿼리문 실행
addrIdInfo = cur.fetchall() # 결과를 addrIdInfo 저장, addrIdInfo에는 index와 실제 address 해시 주소가 저장

cur.execute("SELECT * FROM TxID") # SELECT 쿼리문 실행
txIdInfo = cur.fetchall() # 결과를 txIdInfo 저장, txIdInfo에는 index와 실제 tx 해시 주소가 저장

conn.close() # 연결 해제