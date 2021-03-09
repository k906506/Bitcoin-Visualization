import sqlite3

def getTagId(userInput): # 입력 값에 따른 tagId 리턴
    if userInput == "업비트":
        return 942
    elif userInput == "빗썸":
        return 167
    elif userInput == "코인원":
        return 390
    else:
        return -1

'''
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
'''

def main():
    conn = sqlite3.connect("dbv3-service.db")
    cur = conn.cursor()

    print("거래소 A를 입력해주세요.")
    srt = input().rstrip()
    userInputSrt = getTagId(srt)

    print("")
    print("거래소 B를 입력해주세요.")
    dst = input().rstrip()
    userInputDst = getTagId(dst)

    print("")
    print("%s와 %s의 모든 주소를 검색합니다." %(srt, dst))

    cur.execute("SELECT Tag.addr FROM Tag where Tag.tag = %d" %userInputSrt)
    tagIdSrt = cur.fetchall()

    cur.execute("SELECT Tag.addr FROM Tag where Tag.tag = %d" %userInputDst)
    tagIdDst = cur.fetchall()
    
    sumClusterInfoSrt = []
    sumClusterInfoDst = []
    sumAddrInfoSrt = []
    sumAddrInfoDst = []
    for addr in tagIdSrt:
        cur.execute("SELECT Cluster.cluster FROM Cluster where Cluster.addr = %d" %addr[0])
        clusterInfo = cur.fetchall()
        sumClusterInfoSrt.extend(clusterInfo)
    for cluster in sumClusterInfoSrt:
        cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster[0])
        addrInfo = cur.fetchall()
        sumAddrInfoSrt.extend(addrInfo)

    print("[%s] 총 %d개의 주소가 검색되었습니다." %(srt, len(sumAddrInfoSrt)))

    for addr in tagIdDst:
        cur.execute("SELECT Cluster.cluster FROM Cluster where Cluster.addr = %d" %addr[0])
        clusterInfo = cur.fetchall()
        sumClusterInfoDst.extend(clusterInfo)
    for cluster in sumClusterInfoDst:
        cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster[0])
        addrInfo = cur.fetchall()
        sumAddrInfoDst.extend(addrInfo)

    print("[%s] 총 %d개의 주소가 검색되었습니다." %(dst, len(sumAddrInfoDst)))

    cur.close()
    conn.close()

    ####################################################################################################
    #1. 위 과정이 종료되면 sumAddrInfoSrt에는 거래소 A의 모든 주소가, sumAddrInfoDst에는 거래소 B의 모든 주소가 저장. #
    ####################################################################################################

    print("")
    print("%s와 %s의 모든 트랜잭션을 검색합니다." %(srt, dst))

    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()

    visitSrt = []
    visitDst = []
    txInfoSrt = {}
    txInfoDst = {}

    for addr in sumAddrInfoSrt: # 거래소 A의 모든 트랜잭션 저장
        cur.execute("SELECT TxOut.tx FROM TxOut INNER JOIN TxIn on TxOut.tx = TxIn.ptx where TxOut.addr = %d" %addr[0])
        try:
            txInfo = cur.fetchone()[0]
        except:
            continue
        if txInfo not in visitSrt:
            txInfoSrt[txInfo] = []
            visitSrt.append(txInfo)
        txInfoSrt[txInfo].append(addr[0])    

    print("[%s]의 총 %s개의 트랜잭션이 검색되었습니다." %(srt, len(txInfoSrt)))

    for addr in sumAddrInfoDst:
        cur.execute("SELECT TxOut.tx FROM TxOut INNER JOIN TxIn on TxOut.tx = TxIn.tx where TxOut.addr = %d" %addr[0])
        try:
            txInfo = cur.fetchone()[0]
        except:
            continue
        if txInfo not in visitDst:
            txInfoDst[txInfo] = []
            visitDst.append(txInfo)
        txInfoDst[txInfo].append(addr[0]) 

    print("[%s]의 총 %s개의 트랜잭션이 검색되었습니다." %(dst, len(txInfoDst)))

    sortTxInfoSrt = sorted(txInfoSrt.items(), key = lambda x : len(x[1]), reverse = True)
    sortTxInfoDst = sorted(txInfoDst.items(), key = lambda x : len(x[1]), reverse = True)

    print("")
    print("주소의 개수가 1개인 트랜잭션을 검색합니다.")

    indexSrt = 0
    indexDst = 0

    for txSrt in sortTxInfoSrt:
        if len(txSrt[1]) == 1:
            break
        indexSrt += 1

    for txDst in sortTxInfoDst:
        if len(txDst[1]) == 1:
            break
        indexDst += 1
    
    print("주소의 개수가 1개인 트랜잭션을 제외합니다.")
    
    newSortTxInfoSrt = []
    newSortTxInfoDst = []
    newSortTxInfoSrt.extend(sortTxInfoSrt[:indexSrt+1])
    newSortTxInfoDst.extend(sortTxInfoDst[:indexDst+1])

    txInfoSrtToDst = {}
    visitSrtToDst = []

    print("")
    print("%s에서 %s로 이동한 트랜잭션을 검색합니다." %(srt, dst))
    for txSrt in newSortTxInfoSrt:
        for txDst in newSortTxInfoDst:
            cur.execute("SELECT count(TxOut.addr) FROM TxOut INNER JOIN TxIn on TxOut.tx = TxIn.tx where TxIn.ptx = %d and TxIn.tx = %d" %(txSrt[0], txDst[0]))
            try:
                txInfo = cur.fetchone()[0]
            except:
                continue
            if txSrt[0] not in visitSrtToDst:
                txInfoSrtToDst[txSrt[0]] = []
                visitSrtToDst.append(txSrt[0])
            txInfoSrtToDst[txSrt[0]].append([txDst[0], txInfo])
            print(txSrt[0], txDst[0], txInfo)
    
    print("")
    print(txInfoSrtToDst)

if __name__ == "__main__":
    main()