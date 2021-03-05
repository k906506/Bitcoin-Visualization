import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

def getTagId(userInput): # 입력 값에 따른 tagId 리턴
    if userInput == "업비트":
        return 942
    elif userInput == "빗썸":
        return 167
    elif userInput == "코인원":
        return 390
    else:
        return -1

def getCluster(tagId): # tagId에 따른 cluster 리턴
    cur.execute("SELECT Tag.addr FROM Tag where Tag.tag = %d" %tagId)
    clusterInfo = cur.fetchall()
    return clusterInfo

def getAddr(cluster): # cluster에 다른 addr 리턴
    cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster)
    addrInfo = cur.fetchall()
    return addrInfo

def getTx(address): # addr에 따른 tx 리턴
    cur.execute("SELECT TxOut.tx FROM TxOut where Txout.addr = %d" %address)
    txInfo = cur.fetchall()
    return txInfo

def getCntTxSrt(tx): # 거래소 A의 tx의 총 주소 개수 리턴
    cur.execute("SELECT TxIn.ptx, count(TxIn.ptx) FROM TxIn where TxIn.ptx = %d" %tx)
    cntInfo = cur.fetchall()
    return cntInfo

def getCntTxDst(tx): # 거래소 B의 tx의 총 주소 개수 리턴
    cur.execute("SELECT TxOut.tx, count(TxOut.tx) FROM TxOut where TxOut.tx = %d" %tx)
    cntInfo = cur.fetchall()
    return cntInfo

def getSrtToDst(txSrt, txDst): # 트랜잭션 간의 거래에서 트랜잭션당 주소 개수 리턴
    cur.execute("SELECT TxIn.ptx, TxOut.tx, count(TxOut.addr) FROM TxIn, TxOut where TxIn.ptx = %d and TxOut.tx = %d" %(txSrt, txDst))
    srtToDstInfo = cur.fetchall()
    return srtToDstInfo

def getDstAddr(tx): # 거래소 B의 트랜잭션당 주소를 거래금액의 내림차순으로 리턴
    cur.execute("SELECT TxOut.addr, TxOut.btc FROM TxOut where TxOut.tx = %d order by btc desc" %tx)
    dstAddrInfo = cur.fetchall()
    return dstAddrInfo

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
        addrInfo = getAddr(cluster)
        sumAddrInfoSrt.extend(addrInfo)
    for cluster in clusterInfoDst:
        addrInfo = getAddr(cluster)
        sumAddrInfoDst.extend(addrInfo)

    #####################################################################################################
    # 1. 위 과정이 종료되면 sumAddrInfoSrt에는 거래소 A의 모든 주소가, sumAddrInfoDst에는 거래소 B의 모든 주소가 저장. #
    #####################################################################################################

    cur.close()
    conn.close()

    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()

    sumTxInfoSrt = []
    sumTxInfoDst = []
    for addr in sumAddrInfoSrt:
        txInfo = getTx(addr)
        if txInfo not in sumTxInfoSrt:
            sumTxInfoSrt.extend(txInfo)
    for addr in sumAddrInfoDst:
        txInfo = getTx(addr)
        if txInfo not in sumTxInfoDst:
            sumTxInfoDst.extend(txInfo)

    sumTxInfoSrt = sorted(sumTxInfoSrt, key = lambda x : -x[1])
    sumTxInfoDrt = sorted(sumTxInfoDrt, key = lambda x : -x[1])

    sumSrtToDstInfo = []
    for txSrt in sumAddrInfoSrt:
        for txDst in sumAddrInfoDst:
            srtToDstInfo = getSrtToDst(txSrt[0], txDst[0])
            sumSrtToDstInfo.extend(srtToDstInfo)

    sumSrtToDstInfo = sorted(sumSrtToDstInfo, key = lambda x : -x[2])

    ###################################################################################################
    # 2. 위 과정이 종료되면 거래소 A의 트랜잭션, 거래소 B의 트랜잭션을 트랜잭션당 주소 개수가 많은 순으로 내림차순으로 정렬. #
    ###################################################################################################