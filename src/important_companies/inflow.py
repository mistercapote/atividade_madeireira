"""Arquivo sobre a construção de fluxo do grafo
Verifica os fluxos possíveis
"""
import pandas as pd
import networkx as nx
import numpy as np
from networkx.classes.function import path_weight
from tqdm import tqdm
from modules import  get_concessions, get_sink_nodes, get_timberflow
from data_cleaner import convert_id_to_str


transportes_janeiro =pd.read_csv('data/df_01.csv') 
# transportes_junho = pd.read_csv('../data/df_06.csv')
transportes_julho = pd.read_csv('data/df_07.csv')
transportes_agosto = pd.read_csv('data/df_08.csv')
transportes_setembro = pd.read_csv('data/df_09.csv')
transportes_outubro= pd.read_csv('data/df_10.csv')
transportes_novembro = pd.read_csv('data/df_11.csv')
transportes_dezembro = pd.read_csv('data/df_12.csv')


tranporte_segundo_semestre= pd.concat([transportes_julho, transportes_agosto, transportes_setembro, transportes_outubro, transportes_novembro, transportes_dezembro], ignore_index=True)


df_tran = tranporte_segundo_semestre[['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes', 'Volume']]
df_tran = df_tran.groupby(['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes'])['Volume'].sum().reset_index()

#  Convertendo todos os nós para str
df_tran = convert_id_to_str(df_tran)

#  Criando dicionario com os tipos de cada empresa

nodes_new = set(df_tran['CPF_CNPJ_Rem']).union(set(df_tran['CPF_CNPJ_Des']))

#  Criando grafo e adicionando nós 
G = nx.DiGraph()
G.add_nodes_from(nodes_new)


# Cria as arestas com base nas transações e com peso = volume
edges = []

for row in df_tran.iterrows():
    # Ignora laços
    if str(row[1]['CPF_CNPJ_Rem']) != str(row[1]['CPF_CNPJ_Des']):
        edges.append((str(row[1]['CPF_CNPJ_Rem']), str(row[1]['CPF_CNPJ_Des']), {'Volume': row[1]['Volume']}))

G.add_edges_from(edges)


emp_type = {}



df_nodes = tranporte_segundo_semestre[['CPF_CNPJ_Rem', 'TpRem']].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ', 'TpRem': 'Tipo'})
df_nodes = pd.concat([df_nodes, tranporte_segundo_semestre[['CPF_CNPJ_Des', 'TpDes']].rename(columns={'CPF_CNPJ_Des': 'CPF_CNPJ', 'TpDes': 'Tipo'})]).drop_duplicates('CPF_CNPJ')
df_pto  = df_tran[(df_tran['TpRem'] == 'PTO_IBAMA') & (df_tran['TpDes'] == 'PTO_IBAMA')].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ'})
df_pto = df_pto.groupby('CPF_CNPJ')['Volume'].sum().reset_index()



origem = tranporte_segundo_semestre[["CPF_CNPJ_Rem", "LatOrigem", "LongOrigem", "TpRem"]].rename(
    columns={
    'CPF_CNPJ_Rem': 'id_emp', 
    'LatOrigem': 'latitude', 
    'LongOrigem': 'longitude', 
    'TpRem': 'type'
})
destino = tranporte_segundo_semestre[["CPF_CNPJ_Des", "LatDestino", "LongDestino", "TpDes"]].rename(
    columns={
    'CPF_CNPJ_Des': 'id_emp', 
    'LatDestino': 'latitude', 
    'LongDestino': 'longitude', 
    'TpDes': 'type'
})

nodes = pd.concat([origem, destino], ignore_index=True)
nodes.drop_duplicates("id_emp", inplace=True)

# nodes.to_csv("nodes.csv", index=False)
for i,node in nodes.iterrows():
  emp_type[str(node['id_emp'])] = node['type']


get_timberflow(G, emp_type)






#  Parte wal sug

df_nodes = tranporte_segundo_semestre[['CPF_CNPJ_Rem', 'TpRem']].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ', 'TpRem': 'Tipo'})
df_nodes = pd.concat([df_nodes, tranporte_segundo_semestre[['CPF_CNPJ_Des', 'TpDes']].rename(columns={'CPF_CNPJ_Des': 'CPF_CNPJ', 'TpDes': 'Tipo'})]).drop_duplicates('CPF_CNPJ')



# Constrói árvores com a raiz sendo o manejo
manejos = set(df_nodes[df_nodes['Tipo'] == 'MANEJO']['CPF_CNPJ'])
finais = set(df_nodes[df_nodes['Tipo'] == 'FINAL']['CPF_CNPJ'])
all_important_patios = set(df_pto_outliers['CPF_CNPJ'])
aux_valid_patios = set()
valid_patios = set()


# Verifica 
for each_manejo in manejos:
    T = nx.bfs_tree(G, each_manejo)
    if finais.intersection(set(T.nodes())) != set():
        # Salva os pátios que são conectados a um manejo
        aux_valid_patios.update(all_important_patios.intersection(set(T.nodes())))

print(len(aux_valid_patios))

# Filtra quais pátios chegam a um final
# for each_patio in aux_valid_patios:
#     T = nx.bfs_tree(G, each_patio)
#     if finais.intersection(set(T.nodes())) != set():
#         # Salva os pátios que são conectados a um final
#         valid_patios.update(aux_valid_patios.intersection(set(T.nodes())))


# Retira os pátios importantes e verifica o fluxo no subgrafo criado
SG = nx.subgraph_view(G, filter_node= lambda x: x != list(aux_valid_patios)[0])
aux = nx.strongly_connected_components(G)
components_aux = {}

# Verifica quais componentes fortemente conexas possuem mais de um vértice
for x in aux:
    if len(x) > 1:
        for patio in aux_valid_patios:
            if patio in x:
                components_aux[patio] = x

print(len(components_aux))
print(components_aux)