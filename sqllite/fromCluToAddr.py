from pyvis.network import Network
import sqlite3
import pandas as pd
import networkx as nx

got_net = Network(height="750px", width="100%")

conn = sqlite3.connect("dbv3-service.db")
cur = conn.cursor()

cur.execute("select * from tagID INNER JOIN Tag on TagID.id = Tag.tag INNER JOIN Cluster on Tag.addr = Cluster.cluster where TAgId.id = 942 limit 100")
# set the physics layout of the network

got_data = cur.fetchall()

for e in got_data:
    src = str(e[5])
    dst = str(e[4])
    w = str(e[3])

    got_net.add_node(src, src, title=src)
    got_net.add_node(dst, dst, title=dst)
    got_net.add_edge(src, dst, value=w)

got_net.show_buttons(filter_=['physics'])
got_net.show("fromCluToAddr.html")