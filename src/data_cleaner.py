import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Guarda os dados do csv num DataFrame
df = pd.read_csv('df_meses\\df_meses\\df_01.csv')

# Separa os dados em três DataFrames: Remetentes, Destinatários e Transações
df_rem = df[['CPF_CNPJ_Rem', 'TpRem']].groupby('CPF_CNPJ_Rem').first().reset_index()
df_des = df[['CPF_CNPJ_Des','TpDes']].groupby('CPF_CNPJ_Des').first().reset_index()
df_tran = df[['CPF_CNPJ_Rem', 'CPF_CNPJ_Des', 'Volume']]
df_tran = df_tran.groupby(['CPF_CNPJ_Rem', 'CPF_CNPJ_Des'])['Volume'].sum().reset_index()

# Cria o grafo direcionado com os vértices sendo os remetentes e destinatários
G = nx.DiGraph()
nodes = set(df_rem['CPF_CNPJ_Rem']).union(set(df_des['CPF_CNPJ_Des']))
G.add_nodes_from(nodes)

# Cria as arestas com base nas transações e com peso = volume
edges = []
for row in df_tran.iterrows():
    if int(row[1]['CPF_CNPJ_Rem']) != int(row[1]['CPF_CNPJ_Des']):
        edges.append((int(row[1]['CPF_CNPJ_Rem']), int(row[1]['CPF_CNPJ_Des']), {'Volume': row[1]['Volume']}))
G.add_edges_from(edges)

print(pd.unique(df_des['TpDes']))
print(pd.unique(df_rem['TpRem']))
print(G.number_of_nodes())

# Plota o grafo
# plt.figure(figsize=(16,23))
# nx.draw(G, node_color='red', node_size=30)
# plt.margins(0.2)
# plt.show()