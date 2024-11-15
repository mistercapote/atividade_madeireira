import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Guarda os dados do csv num DataFrame
df = pd.read_csv('..\\data\\df_01.csv')

#TODO: Se livrar do df_rem e df_des e criar um com apenas as informacoes dos patios

# Separa os dados em três DataFrames: Remetentes, Destinatários e Transações
#df_rem = df[['CPF_CNPJ_Rem', 'TpRem']].groupby('CPF_CNPJ_Rem').first().reset_index()
#df_des = df[['CPF_CNPJ_Des','TpDes']].groupby('CPF_CNPJ_Des').first().reset_index()
df_tran = df[['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes', 'Volume']]
df_tran = df_tran.groupby(['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes'])['Volume'].sum().reset_index()

# Cria o grafo direcionado com os vértices sendo os remetentes e destinatários
nodes = set(df_tran['CPF_CNPJ_Rem']).union(set(df_tran['CPF_CNPJ_Des']))
G = nx.DiGraph()
G.add_nodes_from(nodes)

# Cria as arestas com base nas transações e com peso = volume
edges = []
for row in df_tran.iterrows():
    # Ignora laços
    if int(row[1]['CPF_CNPJ_Rem']) != int(row[1]['CPF_CNPJ_Des']):
        edges.append((int(row[1]['CPF_CNPJ_Rem']), int(row[1]['CPF_CNPJ_Des']), {'Volume': row[1]['Volume']}))
G.add_edges_from(edges)

print(G.number_of_nodes())
print(G.number_of_edges())


#TODO: Verificar a soma do volume de transacoes entre dois patios

df_pto = df_tran[(df_tran['TpRem'] == 'PTO_IBAMA') & (df_tran['TpDes'] == 'PTO_IBAMA')]
print(df_pto)
df_pto = df_pto.groupby('CPF_CNPJ_Rem')['Volume'].sum().reset_index()
print(df_pto)

# Dados das transacoes
median = df_pto['Volume'].median()
q1 = df_pto['Volume'].quantile(0.25)
q3 = df_pto['Volume'].quantile(0.75)
ls = median + 1.5*(q3-q1)
print('#'*40)
print(f"Median: {median}, Q1: {q1}, Q3: {q3}, LS: {ls}")
df_pto = df_pto[df_pto['Volume'] > ls]


# Plota o grafo
# plt.figure(figsize=(16,23))
# nx.draw(G, node_color='red', node_size=30)
# plt.margins(0.2)
# plt.show()