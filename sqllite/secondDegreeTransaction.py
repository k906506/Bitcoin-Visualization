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

    print("탐색할 차수를 입력해주세요.")
    print("ex) 1차 : 거래소 A -> 거래소 B / 2차 : 거래소 A -> 거래소 B -> 거래소 C")
    degree = int(input())

    print("")
    userInputId = list()
    stringUserInput = list()
    for i in range(0, degree+1):
        print("거래소 %s를 입력해주세요." %chr(65+i))
        userInput = input().rstrip()
        stringUserInput.append(userInput)
        userInput = getTagId(userInput)
        while userInput == -1:
            userInput = input().rstrip()
            userInput = getTagId(userInput)
        userInputId.append(userInput)
    
    checkVisit = dict()
    for i in userInputId:
        if i not in checkVisit:
            checkVisit[i] = False
    
    sumAddrInfo = dict()
    for tagId in userInputId:
        if checkVisit[tagId]:
            continue
        else:
            sumAddrInfo[tagId] = []
            clusterInfo = []
            cur.execute("SELECT Tag.addr FROM Tag where Tag.tag = %d" %tagId)
            tagIdInfo = cur.fetchall()
            for addr in tagIdInfo:
                cur.execute("SELECT Cluster.cluster FROM Cluster where Cluster.addr = %d" %addr[0])
                clusterInfo.extend(cur.fetchall())
            for cluster in clusterInfo:
                cur.execute("SELECT Cluster.addr FROM Cluster where Cluster.cluster = %d" %cluster[0])
                sumAddrInfo[tagId].extend(cur.fetchall())

    cur.close()
    conn.close()

    ###########################################################
    # 1. 위 과정이 종료되면 sumAddrInfo에 거래소별로 모든 addr이 저장. #
    ###########################################################

    print("")
    print("트랜잭션 탐색을 진행합니다.")

    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()

    newSortTxInfo = dict()
    txInfoInTagId = dict()

    for element in userInputId:
        checkVisit[element] = False

    for tagId in userInputId:
        if checkVisit[tagId]:
            continue
        else:
            sumTxInfo = dict()
            visitTx = list()
            for addr in sumAddrInfo[tagId]:
                cur.execute("SELECT TxOut.tx FROM TxOut where TxOut.addr = %d" %addr[0])
                try:
                    txInfo = cur.fetchone()[0]
                except:
                    continue
                if txInfo not in visitTx:
                    sumTxInfo[txInfo] = []
                    visitTx.append(txInfo)
                sumTxInfo[txInfo].append(addr[0])
            
            sortTxInfo = sorted(sumTxInfo.items(), key = lambda x : len(x[1]), reverse = True)

            index = 0
            for tx in sortTxInfo:
                if len(tx[1]) == 10: # 탐색 속도 향상을 위해 주소의 개수가 10개 이하인 tx는 제외
                    break
                index += 1

            sortTxInfo = sortTxInfo[:index+1]
            newSortTxInfo[tagId] = sortTxInfo
            txInfoInTagId[tagId] = list(sumTxInfo.keys())

    print("트랜잭션 탐색을 종료되었습니다.")

    ##################################################################################
    # 2. 위 과정이 종료되면 newSortTxInfo에 거래소별로 [tx, (addr1, addr2, ...)] 형태로 저장. #
    ##################################################################################

    txid = newSortTxInfo[tagId][0][0]
    changeTx = list()
    changeTx.append(txid)

    for i in range(degree):
        visitTx = list()
        ptx = dict()

        cur.execute("SELECT TxIn.tx FROM TxIn where TxIn.ptx = %d order by TxIn.n desc" %(txid)) # ptx가 가장 많은 주소를 가진 tx.
        try:
            txInfo = cur.fetchall()
        except:
            continue
        for tx in txInfo:
            if tx[0] not in visitTx:
                ptx[tx[0]] = 1
                visitTx.append(tx[0])
            ptx[tx[0]] += 1
        
        sortPtx = sorted(ptx.items(), key = lambda x : -x[1])
        for element in sortPtx:
            if element[0] in txInfoInTagId[tagId]:
                txid = sortPtx[0][0]
                changeTx.append(txid)
                break

    ##################################################
    # 3. 위 과정이 종료되면 changeTx에 tx 이동 경로가 저장. #
    ##################################################

    SecondDimGraph = Network(height="750px", width="100%")

    for i in range(degree):
        srtGraph = str("[%s] Tx : %d" %(stringUserInput[i], changeTx[0]))
        SecondDimGraph.add_node(srtGraph, srtGraph, title = srtGraph)
    try:
        for i in range(len(sumTxInfo[changeTx[degree]])):
            dstGraph = str("[%s] Addr : %d" %(stringUserInput[len(stringUserInput)-1], sumTxInfo[changeTx[degree]][i]))
            w = str(1)
            SecondDimGraph.add_node(dstGraph, dstGraph, title = dstGraph)
            SecondDimGraph.add_edge(srtGraph, dstGraph, value = w)

        SecondDimGraph.show_buttons(filter_=['physics'])
        SecondDimGraph.show("secondTransaction.html")
    except:
        print("조회된 정보가 없습니다.")
if __name__ == "__main__":
    main()