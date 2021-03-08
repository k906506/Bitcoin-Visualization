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
    cur.execute("SELECT TxOut.tx FROM TxOut where TxOut.addr = %d" %address)
    txInfo = cur.fetchone()
    return txInfo[0]

def getCntTxSrt(tx): # 거래소 A의 tx의 총 주소 개수 리턴
    cur.execute("SELECT TxIn.ptx FROM TxIn where TxIn.ptx = %d" %tx)
    cntInfo = cur.fetchone()
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

    print("거래소 A를 입력해주세요.")
    userInputSrt = getTagId(input().rstrip())

    print("거래소 B를 입력해주세요.")
    userInputDst = getTagId(input().rstrip())

    print("첫번째 과정을 진행합니다.")

    cur.execute("SELECT Tag.addr FROM Tag where Tag.tag = %d" %userInputSrt)
    tagIdSrt = cur.fetchone()[0]

    cur.execute("SELECT Tag.addr FROM Tag where Tag.tag = %d" %userInputDst)
    tagIdDst = cur.fetchone()[0]

    cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %tagIdSrt)
    clusterInfoSrt = cur.fetchall()

    cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %tagIdDst)
    clusterInfoDst = cur.fetchall()
    
    sumAddrInfoSrt = []
    sumAddrInfoDst = []
    for cluster in clusterInfoSrt:
        cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster)
        addrInfo = cur.fetchall()
        sumAddrInfoSrt.extend(addrInfo)
    for cluster in clusterInfoDst:
        cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster)
        addrInfo = cur.fetchall()
        sumAddrInfoDst.extend(addrInfo)
    
    print(sumAddrInfoDst)

    cur.close()
    conn.close()

    print("거래소 A와 거래소 B의 모든 주소가 검색되었습니다.")

    print(input())
    ####################################################################################################
    #1. 위 과정이 종료되면 sumAddrInfoSrt에는 거래소 A의 모든 주소가, sumAddrInfoDst에는 거래소 B의 모든 주소가 저장. #
    ####################################################################################################

    print("두번째 과정을 진행합니다.")

    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()

    txInfoSrt = []
    txInfoDst = []
    sumTxInfoSrt = {}
    sumTxInfoDst = {}
    for addr in sumAddrInfoSrt:
        cur.execute("SELECT TxOut.tx FROM TxOut where TxOut.addr = %d" %addr)
        try:
            txInfo = cur.fetchone()[0]
        except:
            continue
        if txInfo not in txInfoSrt:
            sumTxInfoSrt[txInfo] = 0
            txInfoSrt.append(txInfo)
        else:
            sumTxInfoSrt[txInfo] += 1
        print(addr)
        print("")
    for addr in sumAddrInfoDst:
        cur.execute("SELECT TxOut.tx FROM TxOut where TxOut.addr = %d" %addr)
        try:
            txInfo = cur.fetchone()[0]
        except:
            continue
        if txInfo not in txInfoDst:
            sumTxInfoDst[txInfo] = 0
            txInfoDst.append(txInfo)
        else:
            sumTxInfoDst[txInfo] += 1
    
    print("트랜잭션 탐색을 완료하셨습니다.")
    listSumTxInfoSrt = sorted(sumTxInfoSrt.items(), reverse=True)
    print(listSumTxInfoSrt)

if __name__ == "__main__":
    main()