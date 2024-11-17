"""Arquivo sobre a construção de fluxo do grafo"""
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

df_tran_jan = transportes_janeiro[['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes', 'Volume']]
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



# Constrói árvores com a raiz sendo o manejo
manejos = set(nodes[nodes['type'] == 'MANEJO']['id_emp'])
finais = set(nodes[df_nodes['type'] == 'FINAL']['id_emp'])
all_important_patios = set(nodes['id_emp'])
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