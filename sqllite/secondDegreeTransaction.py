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

    print("탐색할 차수를 입력해주세요. ex) 1차 : 거래소 A -> 거래소 B / 2차 : 거래소 A -> 거래소 B -> 거래소 C")
    degree = int(input())

    userInputId = list()
    stringUserInput = list()
    for i in range(0, degree+1):
        print("거래소 %s를 입력해주세요." %chr(97+i))
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

    ##########################################################
    # 1. 위 과정이 종료되면 sumAddrInfo에 거래소 별 모든 주소가 저장. #
    ##########################################################

    print("")
    print("트랜잭션 탐색을 진행합니다.")

    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()

    sumTxInfo = dict()
    newSortTxInfo = dict()

    for element in checkVisit:
        element = False

    i = 0
    for tagId in userInputId:
        if checkVisit[tagId]:
            continue
        else:
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
                if len(tx[1]) == 1:
                    break
                index += 1

            sortTxInfo = sortTxInfo[:index+1]
            newSortTxInfo[tagId] = sortTxInfo

            checkVisit[tagId] = True

            print("%s의 트랜잭션 탐색을 완료했습니다." %stringUserInput[i])
            i += 1
            print(len(newSortTxInfo[tagId]))

    

    ############################################################
    #2. 위 과정이 종료되면 newSortTxInfo에는 거래소 별 tx - addr 저장. #
    ############################################################

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

if __name__ == "__main__":
    main()