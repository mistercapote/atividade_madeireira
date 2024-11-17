import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

G = nx.MultiDiGraph()
nodes = pd.read_csv("nodes.csv", low_memory=False)
edges = pd.read_csv("edges.csv", low_memory=False)

for i, node in nodes.iterrows():
    G.add_node(node["CPF_CNPJ"], type=node["Tipo"], attr=node["Coordenada"])

for i, edge in edges.iterrows():
    G.add_edge(edge["CPF_CNPJ_Rem"], edge["CPF_CNPJ_Des"], weight=-edge["Volume"], attr=edge["DtEmissao"])

print(G.number_of_nodes())
print(G.number_of_edges())

G_original = G.copy()
G_reverso = G.reverse().copy()
G = G_reverso.copy()











