import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Guarda os dados do csv num DataFrame
df = pd.read_csv('..\\data\\df_01.csv')


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

# DataFrame com as transações apenas entre dois pátios
df_pto = df_tran[(df_tran['TpRem'] == 'PTO_IBAMA') & (df_tran['TpDes'] == 'PTO_IBAMA')]
df_pto = df_pto.groupby('CPF_CNPJ_Rem')['Volume'].sum().reset_index()

# Dados das transacoes
median = df_pto['Volume'].median()
q1 = df_pto['Volume'].quantile(0.25)
q3 = df_pto['Volume'].quantile(0.75)
ls = median + 1.5*(q3-q1)
df_pto = df_pto[df_pto['Volume'] > ls]

# Verifica as componentes conexas antes e depois de retirar os vertices
print(nx.number_weakly_connected_components(G))
components = []
for node in list(df_pto['CPF_CNPJ_Rem']):
    SG = nx.subgraph_view(G, filter_node= lambda x: x != node)
    components.append(nx.number_weakly_connected_components(SG))

df_pto['Conected_Components'] = components
print(df_pto)


# Plota o grafo
# plt.figure(figsize=(16,23))
# nx.draw(G, node_color='red', node_size=30)
# plt.margins(0.2)
# plt.show()