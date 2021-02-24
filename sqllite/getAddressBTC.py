import sqlite3

conn = sqlite3.connect("dbv3-service.db")
cur = conn.cursor()

def returnTagId(tagId):
    if tagId == "업비트":
        return 942
    elif tagId == "빗썸":
        return 167
    elif tagId == "코인원":
        return 390
    else:
        return -1

def main():
    userInput = input().rstrip()
    tag = returnTagId(userInput)      
    cur.execute("SELECT Tag.tag, Cluster.cluster, Cluster.addr FROM TagID INNER JOIN Tag on TagID.id = Tag.tag INNER JOIN Cluster on Tag.addr = Cluster.cluster where TagID.id = %d" %tag)
    tagInfo = cur.fetchall()

if __name__ == "__main__":
    main()