import sqlite3
from pyvis.network import Network
import networkx as nx

def returnTypeOfInput(input): # 입력한 해시값의 유효성 판단
    if len(input) == 64:
        return 0
    elif len(input) == 42:
        return 1
    else:
        return -1

def returnIntFromHash(inputType, inputHash): # 입력한 해시값을 Int Index로 변환
    conn = sqlite3.connect("dbv3-index.db")
    cur = conn.cursor()
    if inputType == 0: #tx의 해시값
        cur.execute("SELECT TxID.id FROM TxID where TxID.txid = ?", (inputHash,))
    else: # addr의 해시값
        cur.execute("SELECT AddrID.id FROM AddrID where AddrID.addr = %s" %inputHash)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

def returnTxFromIndex(inputType, infoIndex): # tx로 변환
    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()
    if inputType == 0: # 이미 tx값이므로 변환 X
        result = infoIndex
    elif inputType == 1: # addr의 해시값
        cur.execute("SELECT TxOut.tx FROM TxOut where TxOut.addr = %d" %infoIndex)
        result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

def returnTxAboutDegree(infoTx, degree): # 차수 직전 tx까지의 연결리스트 변환 (ptx까지만)
    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()
    tx_list = []
    if degree == 1:
        tx_list.append(infoTx)
    else:
        tx_list.append(infoTx)
        for _ in range(degree-1):
            cur.execute("SELECT TxIn.tx FROM TxIn where TxIn.ptx = %d" %infoTx)
            tx = cur.fetchone()[0]
            tx_list.append(tx)
            infoTx = tx
    cur.close()
    conn.close()
    return tx_list

def returnBTCAboutTx(tx_list):
    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()

    btcAndTx_list = list()
    for tx in tx_list:
        cur.execute("SELECT sum(TxOut.btc) FROM TxOut where TxOut.tx = %d" %tx)
        btc = cur.fetchone()[0]
        btcAndTx_list.append((tx, btc))
    
    return btcAndTx_list

def returnAddrFromTx(infoPtx): # Tx를 통해 Addr을 리턴
    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()
    cur.execute("SELECT TxOut.addr, TxOut.btc FROM TxOut where TxOut.tx = %d order by TxOut.btc desc" %infoPtx) # Addr을 btc 금액값에 따라 내림차순으로 정렬
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def makeGraph(tx_list, infoAddrAndBtc, degree):
    graph = Network(height="750px", width="100%")

    if degree == 1:
        for tx in tx_list:
            graph.add_node(tx, tx, title = str(tx))

        for i in range(len(tx_list)-1):
            graph.add_edge(tx_list[i], tx_list[i+1], value = 1)

        ptx = str(tx_list[len(tx_list)-1])
        for addr in infoAddrAndBtc:
            dstGraph = str(addr[0])
            btc = addr[1]
            graph.add_node(dstGraph, dstGraph, title = str(dstGraph))
            graph.add_edge(ptx, dstGraph, value = btc)
    
    else:
        src_tx = str("[Tx] : %s" %tx_list[0][0])
        graph.add_node(src_tx, src_tx, title = src_tx, color = '#000000')

        for i in range(1, len(tx_list)):
            mid_tx = str("[Tx] : %s" %tx_list[i][0])
            graph.add_node(mid_tx, mid_tx, title = mid_tx, color = '#b4b4b4')
        
        for i in range(len(tx_list)-1):
            mid_ptx = str("[Tx] : %s" %tx_list[i][0])
            mid_tx = str("[Tx] : %s" %tx_list[i+1][0])
            graph.add_edge(mid_ptx, mid_tx, value = tx_list[i+1][1])
    
        ptx = str("[Tx] : %s" %tx_list[len(tx_list)-1][0])
        for addr in infoAddrAndBtc:
            dstGraph = str("[Addr] : %s" %addr[0])
            btc = addr[1]
            graph.add_node(dstGraph, dstGraph, title = dstGraph, color = '#000000')
            graph.add_edge(ptx, dstGraph, value = btc)


    graph.show_buttons(filter_=['physics'])
    graph.show("inputHashOutputGraph.html")

def main():
    print("해시값을 입력해주세요.")
    InputHash = input().rstrip()
    print("차수를 입력해주세요.")
    degree = int(input())

    inputType = returnTypeOfInput(InputHash)
    while inputType == -1:
        print("해시값이 잘못되었습니다. 정상적인 값을 입력해주세요.")
        InputHash = input().rstrip()
        inputType = returnTypeOfInput(InputHash)
    
    infoIndex = returnIntFromHash(inputType, InputHash) # Int Index로 변환
    infoTx = returnTxFromIndex(inputType, infoIndex) # tx로 변환
    tx_list = returnTxAboutDegree(infoTx, degree) # ptx까지 리스트에 저장
    infoPtx = tx_list[len(tx_list)-1] # ptx 저장`
    infoAddrAndBtc = returnAddrFromTx(infoPtx) # ptx로 addr 저장
    if degree == 1:
        makeGraph(tx_list, infoAddrAndBtc, degree) # 그래프로 변환
    else:
        btcAndTx_list = returnBTCAboutTx(tx_list)
        makeGraph(btcAndTx_list, infoAddrAndBtc, degree)

if __name__ == "__main__":
    main()