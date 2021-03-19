from pyvis.network import Network
import sqlite3
import pandas as pd
import networkx as nx

def getTagId(userInput): # 입력 값에 따른 tagId 리턴
    if userInput == "업비트":
        return 942
    elif userInput == "빗썸":
        return 167
    elif userInput == "코인원":
        return 390
    else:
        return -1

def main():
    conn = sqlite3.connect("dbv3-service.db")
    cur = conn.cursor()

    print("탐색할 차수 1차 : 거래소 A -> 거래소 B / 2차 : 거래소 A -> 거래소 B -> 거래소 C")
    degree = int(input())

    userInputId = []
    for i in range(0, degree+1):
        print("거래소 %s를 입력해주세요." %chr(97+i))
        userInput = input().rstrip()
        userInput = getTagId(userInput)
        while userInput == -1:
            userInput = input().rstrip()
            userInput = getTagId(userInput)
        userInputId.append(userInput)
    
    sumAddrInfo = dict()
    for tagId in userInputId:
        sumAddrInfo[tagId] = []
        cur.execute("SELECT Tag.addr FROM Tag where Tag.tag = %d" %tagId)
        tagIdInfo = cur.fetchall()
        for addr in tagIdInfo:
            cur.execute("SELECT Cluster.cluster FROM Cluster where Cluster.addr = %d" %addr[0])
            clusterInfo = cur.fetchall()
            for cluster in clusterInfo:
                cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster[0])
                addrInfo = cur.fetchall()
                sumAddrInfo[tagid].extend(addrInfo)

    for tagId in userInputId:
        print(len(sumAddrInfo[tagId]))

    """     
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

    if notEqualSrtDst:
        for addr in tagIdDst:
            cur.execute("SELECT Cluster.cluster FROM Cluster where Cluster.addr = %d" %addr[0])
            clusterInfo = cur.fetchall()
            sumClusterInfoDst.extend(clusterInfo)
        for cluster in sumClusterInfoDst:
            cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster[0])
            addrInfo = cur.fetchall()
            sumAddrInfoDst.extend(addrInfo)
    else:
        sumClusterInfoDst = sumClusterInfoSrt
        sumAddrInfoDst = sumAddrInfoSrt

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

    for addr in sumAddrInfoSrt:
        cur.execute("SELECT TxOut.tx FROM TxOut where TxOut.addr = %d" %addr[0])
        try:
            txInfo = cur.fetchone()[0]
        except:
            continue
        if txInfo not in visitSrt:
            txInfoSrt[txInfo] = []
            visitSrt.append(txInfo)
        txInfoSrt[txInfo].append(addr[0])    

    print("[%s] 총 %s개의 트랜잭션이 검색되었습니다." %(srt, len(txInfoSrt)))

    for addr in sumAddrInfoDst:
        cur.execute("SELECT TxOut.tx FROM TxOut where TxOut.addr = %d" %addr[0])
        try:
            txInfo = cur.fetchone()[0]
        except:
            continue
        if txInfo not in visitDst:
            txInfoDst[txInfo] = []
            visitDst.append(txInfo)
        txInfoDst[txInfo].append(addr[0]) 

    print("[%s] 총 %s개의 트랜잭션이 검색되었습니다." %(dst, len(txInfoDst)))

    sortTxInfoSrt = sorted(txInfoSrt.items(), key = lambda x : len(x[1]), reverse = True)
    sortTxInfoDst = sorted(txInfoDst.items(), key = lambda x : len(x[1]), reverse = True)

    #####################################################################################################
    #2. 위 과정이 종료되면 txInfoSrt에는 거래소 A의 tx별 addr 주소가, txInfoDst에는 거래소 B의 tx별 addr 주소가 저장. #
    #####################################################################################################

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
    print("%s에서 %s으로 이동한 트랜잭션을 검색합니다." %(srt, dst))
    for txSrt in newSortTxInfoSrt:
        for txDst in newSortTxInfoSrt:
            cur.execute("SELECT count(TxOut.addr), sum(TxOut.btc) FROM TxOut INNER JOIN TxIn on TxOut.tx = TxIn.tx where TxIn.ptx = %d and TxOut.tx = %d" %(txSrt[0], txDst[0]))
            try:
                txInfo = cur.fetchone()
            except:
                continue
            if txInfo[0] == 0:
                continue
            else:
                if txSrt[0] not in visitSrtToDst:
                    txInfoSrtToDst[txSrt[0]] = []
                    visitSrtToDst.append(txSrt[0])
                txInfoSrtToDst[txSrt[0]].append([txDst[0], txInfo[0], txInfo[1]])
    
    print("총 %d개의 트랜잭션이 검색되었습니다." %len(txInfoSrtToDst))

    print("")
    print("(1) 주소의 개수가 많고, (2) 총 거래 금액이 높은 트랜잭션부터 내림차순으로 정렬합니다.")

    txInfoSrtToDst = sorted(txInfoSrtToDst.items(), key = lambda x : (x[1][0][1], x[1][0][2]), reverse = True)

    ###############################################################################################
    #3. 위 과정이 종료되면 txInfoSrtToDst에는 거래소 A -> 거래소 B의 tx가 주소 개수, 거래 금액 내림차순으로 정렬. #
    ###############################################################################################

    index = 1
    for element in txInfoSrtToDst:
        print("[%3d] [TxOut] %9d [TxIn] %9d [Addr Cnt] %3d [BTC] %10.10f" %(index, element[0], element[1][0][0], element[1][0][1], element[1][0][2]))
        index += 1

    print("")
    print("탐색할 트랜잭션의 INDEX를 입력해주세요.")
    index = int(input())

    print("")
    print("%d번째의 거래를 출력합니다." %index)

    infoSrtToDst = txInfoSrtToDst[index-1]
    cur.execute("SELECT TxOut.addr, TxOut.btc FROM TxOut INNER JOIN TxIn on TxOut.tx = TxIn.tx where TxIn.ptx = %d and TxOut.tx = %d" %(infoSrtToDst[0], infoSrtToDst[1][0][0]))
    info = cur.fetchall()

    index = 1
    for element in info:
        print("[%3d] [TxOut] %9d [TxIn] %9d [Addr] %9d [BTC] %10.10f" %(index, infoSrtToDst[0], infoSrtToDst[1][0][0], element[0], element[1]))
        index += 1
    
    firstDimGraph = Network(height="750px", width="100%")

    srtGraph = str("[%s] Tx : %d" %(srt, infoSrtToDst[0]))
    firstDimGraph.add_node(srtGraph, srtGraph, title = srtGraph)
    for element in info:
        dstGraph = str("[%s] Addr : %d" %(dst, element[0]))
        w = str(element[1])
        firstDimGraph.add_node(dstGraph, dstGraph, title = dstGraph)
        firstDimGraph.add_edge(srtGraph, dstGraph, value = w)

    firstDimGraph.show_buttons(filter_=['physics'])
    firstDimGraph.show("firstTransaction.html")
    """

if __name__ == "__main__":
    main()