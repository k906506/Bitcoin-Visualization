import sqlite3
from pyvis.network import Network

def main():
    G = Network(height="750px", width="100%", directed=True) # 방향성 그래프 생성
    G.add_node("Main", "Main", color='#FF0000')
    count = dict()
    node = list()
    result = list()

    countGreen = 0
    countBlue = 0

    addr_list = []
    for _ in range(10):
        addr_list.append(input())

    for i in range(10):
        conn = sqlite3.connect("dbv3-index.db")
        cur = conn.cursor()

        # 1. 입력한 해시값을 indexAddrId 타입으로 변경한다.
        cur.execute("SELECT AddrId.id FROM AddrID WHERE AddrID.addr = ?", (addr_list[i],))
        try:
            indexAddrId = cur.fetchone()[0]
        except:
            continue
        G.add_node(indexAddrId, indexAddrId, color='#FF0000')
        G.add_edge(indexAddrId, "Main")

        cur.close()
        conn.close()

        conn = sqlite3.connect("dbv3-core.db")
        cur = conn.cursor()

        # 2. TxOut의 addr이 indexAddrId인 트랜잭션을 탐색한다.
        cur.execute("SELECT TxOut.tx FROM TxOut WHERE TxOut.addr = ? LIMIT 20", (indexAddrId,))
        oneDegreeTx = cur.fetchall()

        # 3. ptx가 oneDegreeTx인 트랜잭션을 탐색한다.
        for ftx in oneDegreeTx:
            cur.execute("SELECT TxIn.ptx FROM TxIn WHERE TxIn.tx = ?", (ftx[0],))
            twoDegreeTx = cur.fetchall() # -> 1차 거래 그래프

            4.  # ptx가 twoDegreeTx인 트랜잭션을 탐색한다.
            for stx in twoDegreeTx:
                if stx not in node:
                    count[stx] = 0
                    node.append(stx)
                    countGreen += 1
                G.add_node(stx[0], stx[0], color='#00FF00')
                result.append(stx)

                G.add_edge(stx[0], indexAddrId)
                cur.execute("SELECT TxIn.ptx FROM TxIn WHERE TxIn.tx = ?", (stx[0],))
                threeDegreeTx = cur.fetchall()  # -> 2차 거래 그래프

                for ttx in threeDegreeTx:
                    count[stx] += 1
                    G.add_node(ttx[0], ttx[0], color='#0000FF')
                    countBlue += 1
                    G.add_edge(ttx[0], stx[0])

        cur.close()
        conn.close()

    ans = sorted(count.items(), key = lambda x : x[1], reverse=True)

    for i in range(len(ans)): # 가중치까지의 초록색 노드 개수
        if ans[i][1] <= 30:
            index = i+1
            break

    print("초록 노드 총 개수 : %d" %countGreen)
    print("파란 노드 총 개수 : %d" %countBlue)
    print("1대1 연결 개수 : %d" %(countGreen-index))
    print("초록색 노드당 파란색 노드 개수 : %f" %((countBlue-(countGreen-index))/(countGreen-index)))

    # G.show_buttons(filter_=['physics'])
    # G.show("visualTransactionForType.html")

    # print(countGreen, countBlue, countBlue/countGreen, countGreen/countBlue)

if __name__ == "__main__":
    main()
