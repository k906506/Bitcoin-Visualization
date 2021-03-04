import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

def getTagId(userInput):
    if userInput == "업비트":
        return 942
    elif userInput == "빗썸":
        return 167
    elif userInput == "코인원":
        return 390
    else:
        return -1

def getCluster(tagId):
    cur.execute("SELECT * FROM Tag where Tag.tag = %d" %tagId)
    clusterInfo = cur.fetchall()
    return clusterInfo

def getAddr(cluster):
    cur.execute("SELECT * FROM Cluster where Cluster.cluster = %d" %cluster)
    addrInfo = cur.fetchall()
    return addrInfo

def getTx(address):
    cur.execute("SELECT * FROM TxOut where Txout.addr = %d order by n desc" %address)
    txInfo = cur.fetchall()
    return txInfo

def getCntTxAddrBTC(address): # 특정 주소의 주소의 총 사용량과 거래 금액 리턴
    cur.execute("SELECT TxOut.tx, count(TxIn.n),TxOut.btc From TxIn INNER JOIN TxOut On TxIn.pn = TxOut.n and TxIn.ptx = TxOut.tx where TxOut.addr = %d" %address)
    cntInfo = cur.fetchall()
    return cntInfo

def main():
    conn = sqlite3.connect("dbv3-service.db")
    cur = conn.cursor()

    userInputSrt = input().rstrip()
    userInputDst = input().rstrip()
    tagIdSrt = getTagId(userInputSrt)
    tagIdDst = getTagId(userInputDst)
    clusterInfoSrt = getCluster(tagIdSrt)
    clusterInfoDst = getCluster(tagIdDst)
    
    sumAddrInfoSrt = []
    sumAddrInfoDst = []
    for cluster in clusterInfoSrt:
        addrInfo = getAddr(cluster[0])
        sumAddrInfoSrt.extend(addrInfo)
    for cluster in clusterInfoDst:
        addrInfo = getAddr(cluster[0])
        sumAddrInfoDst.extend(addrInfo)

    #####################################################################################################
    # 1. 위 과정이 종료되면 sumAddrInfoSrt에는 거래소 A의 모든 주소가, sumAddrInfoDst에는 거래소 B의 모든 주소가 저장. #
    #####################################################################################################

    cur.close()
    conn.close()

    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()



    


