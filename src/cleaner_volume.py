import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from auxiliar import *
import glob


# Guarda os dados dos csvs num DataFrame
path = '..\\data'
csv_files = glob.glob(path + '/*.csv')
df = pd.concat(map(pd.read_csv, glob.glob(path + "/*.csv")))

# Separa os dados das transações somando o volume das duplicadas
df_tran = df[['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes', 'Volume']]
df_tran = df_tran.groupby(['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes'])['Volume'].sum().reset_index()
df_nodes = df[['CPF_CNPJ_Rem', 'TpRem']].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ', 'TpRem': 'Tipo'})
df_nodes = pd.concat([df_nodes, df[['CPF_CNPJ_Des', 'TpDes']].rename(columns={'CPF_CNPJ_Des': 'CPF_CNPJ', 'TpDes': 'Tipo'})]).drop_duplicates('CPF_CNPJ')
df_nodes.to_csv('..\\nodes.csv')

# Dicionario com CPF_CNPJ das empresas e seus respectivos tipos
emps = {}
for i,node in df_nodes.iterrows():
    emps[node['CPF_CNPJ']] = node['Tipo']

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

GC = G.copy()
# get_timberflow(GC, emps)

# DataFrame com as transações apenas entre dois pátios
df_pto = df_tran[(df_tran['TpRem'] == 'PTO_IBAMA') & (df_tran['TpDes'] == 'PTO_IBAMA')].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ'})
df_pto = df_pto.groupby('CPF_CNPJ')['Volume'].sum().reset_index()

# Dados das transacoes
median = df_pto['Volume'].median()
q1 = df_pto['Volume'].quantile(0.25)
q3 = df_pto['Volume'].quantile(0.75)
ls = median + 1.5*(q3-q1)

# DataFrame com apenas as empresas importantes de acordo com o volume
df_pto = df_pto[df_pto['Volume'] > ls]

# Verifica as componentes conexas antes e depois de retirar os vertices
print(nx.number_weakly_connected_components(G))
components = []
for node in list(df_pto['CPF_CNPJ']):
    SG = nx.subgraph_view(G, filter_node= lambda x: x != node)
    components.append(nx.number_weakly_connected_components(SG))

df_pto['Conected_Components'] = components

# Constrói árvores com a raiz sendo o manejo
manejos = set(df_nodes[df_nodes['Tipo'] == 'MANEJO']['CPF_CNPJ'])
finais = set(df_nodes[df_nodes['Tipo'] == 'FINAL']['CPF_CNPJ'])
all_important_patios = set(df_pto['CPF_CNPJ'])
valid_patios = set()

# Verifica quais manejos chegam a pelo menos um final 
for each_manejo in manejos:
    T = nx.bfs_tree(G, each_manejo)
    if finais.intersection(set(T.nodes())) != set():
        # Salva os pátios que são conectados a um manejo e a um final
        valid_patios.update(all_important_patios.intersection(set(T.nodes())))

# Retira os pátios importantes e verifica o fluxo no subgrafo criado
for each_valid_patio in valid_patios():
    SG = nx.Subgraph