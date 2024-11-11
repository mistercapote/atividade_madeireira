import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Guarda os dados do csv num DataFrame
df = pd.read_csv('..\\data\\df_01.csv')

# Separa os dados em três DataFrames: Remetentes, Destinatários e Transações
df_rem = df[['CPF_CNPJ_Rem', 'TpRem']].groupby('CPF_CNPJ_Rem').first().reset_index()
df_des = df[['CPF_CNPJ_Des','TpDes']].groupby('CPF_CNPJ_Des').first().reset_index()
df_tran = df[['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes', 'Volume']]
df_tran = df_tran.groupby(['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes'])['Volume'].sum().reset_index()

# Cria o grafo direcionado com os vértices sendo os remetentes e destinatários
nodes = set(df_rem['CPF_CNPJ_Rem']).union(set(df_des['CPF_CNPJ_Des']))
G = nx.DiGraph()
G.add_nodes_from(nodes)

# Cria as arestas com base nas transações e com peso = volume
edges = []
for row in df_tran.iterrows():
    # Ignora lacos
    if int(row[1]['CPF_CNPJ_Rem']) != int(row[1]['CPF_CNPJ_Des']):
        edges.append((int(row[1]['CPF_CNPJ_Rem']), int(row[1]['CPF_CNPJ_Des']), {'Volume': row[1]['Volume']}))
G.add_edges_from(edges)

print(pd.unique(df_des['TpDes']))
print(pd.unique(df_rem['TpRem']))
print(G.number_of_nodes())
print(G.number_of_edges())


#TODO: Verificar a soma do volume de transacoes entre dois patios

# Dados das transacoes
median = df_tran['Volume'].median()
q1 = df_tran['Volume'].quantile(0.25)
q3 = df_tran['Volume'].quantile(0.75)
ls = median + 1.5*(q3-q1)
print('#'*40)
print(f"Median: {median}, Q1: {q1}, Q3: {q3}, LS: {ls}")
print(df_tran[df_tran['Volume'] > ls])

# Plota o grafo
# plt.figure(figsize=(16,23))
# nx.draw(G, node_color='red', node_size=30)
# plt.margins(0.2)
# plt.show()