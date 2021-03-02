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

def main():
    conn = sqlite3.connect("dbv3-service.db")
    cur = conn.cursor()

    userInput = input().rstrip()
    tagId = getTagId(userInput)
    clusterInfo = getCluster(tagId)
    
    sumAddrInfo = []
    for cluster in clusterInfo:
        addrInfo = getAddr(cluster[0])
        sumAddrInfo.extend(addrInfo)
    
    cur.close()
    conn.close()

    conn = sqlite3.connect("dbv3-core.db")
    cur = conn.cursor()

    


