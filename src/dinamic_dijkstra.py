import networkx as nx
import pandas as pd

nodes = pd.read_csv("nodes.csv", low_memory=False)
edges = pd.read_csv("edges.csv", low_memory=False)



G = nx.DiGraph()

for i, edges in edges.iterrows():
    pass





