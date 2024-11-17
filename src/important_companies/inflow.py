"""Arquivo sobre a construção de fluxo do grafo"""
import pandas as pd
import networkx as nx
import numpy as np
from networkx.classes.function import path_weight
from tqdm import tqdm
from modules import create_graph, get_concessions, get_sink_nodes, get_timberflow
from data_cleaner import convert_id_to_str


transportes_janeiro =pd.read_csv('data/df_01.csv') 
# transportes_junho = pd.read_csv('../data/df_06.csv')
transportes_julho = pd.read_csv('data/df_07.csv')
transportes_agosto = pd.read_csv('data/df_08.csv')
transportes_setembro = pd.read_csv('data/df_09.csv')
transportes_outubro= pd.read_csv('data/df_10.csv')
transportes_novembro = pd.read_csv('data/df_11.csv')
transportes_dezembro = pd.read_csv('data/df_12.csv')


# Teste com mês de Janeiro-
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
nodes = pd.read_csv('data/nodes.csv')


for i,node in nodes.iterrows():
  emp_type[node['CPF_CNPJ']] = node['Tipo']


get_timberflow(G, emp_type)


# Apenas com janeiro
print("Apenas com janeiro: ")

emp_type_jan = {}
nodes_jan = pd.read_csv('data/nodes_janeiro.csv')


for i,node in nodes_jan.iterrows():
  emp_type_jan[node['CPF_CNPJ']] = node['Tipo']


