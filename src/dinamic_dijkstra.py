import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import time

a = time.time()
nodes = pd.read_csv("nodes.csv", low_memory=False)
edges = pd.read_csv("edges.csv", low_memory=False)

G = nx.MultiDiGraph()

for i, node in nodes.iterrows():
    G.add_node(node["CPF_CNPJ"], type=node["Tipo"], attr=node["Coordenada"])

for i, edge in edges.iterrows():
    G.add_edge(edge["CPF_CNPJ_Rem"], edge["CPF_CNPJ_Des"])


print(G.number_of_nodes())
print(G.number_of_edges())


plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)

nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=700, font_size=15, edge_color='blue', arrows=True)

edge_labels = {(u, v): d['Volume'] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
b = time.time()
print("Tempo", b-a)
plt.show()





