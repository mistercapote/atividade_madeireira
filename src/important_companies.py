import pandas as pd
import networkx as nx
import numpy as np
from networkx.classes.function import path_weight
from tqdm import tqdm

from data_cleaner import convert_id_to_str

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


#  Empresas do tipo Patio que transportam para empresas do tipo pátio
df_pto = df_tran[(df_tran['TpRem'] == 'PTO_IBAMA') & (df_tran['TpDes'] == 'PTO_IBAMA')]
df_pto = df_pto.groupby('CPF_CNPJ_Rem')['Volume'].sum().reset_index()


nodes_pto = set(df_pto['CPF_CNPJ_Rem'])


emp_pto_degree = {}

for node in nodes_pto:
    emp_pto_degree[node]= G.degree(node)

graus = list(emp_pto_degree.values())


# print(f"Grau:    {graus}")
q1 = np.quantile(graus, 0.25)  # Primeiro quartil (25%)
q2 = np.quantile(graus, 0.5)   # Segundo quartil (50%, ou mediana)
q3 = np.quantile(graus, 0.75)  # Terceiro quartil (75%)
interquartil = q3-q1
limite_superior = q3 + 1.5*interquartil
print(f"Q1 (25%): {q1}")
print(f"Q2 (50% - Mediana): {q2}")
print(f"Q3 (75%): {q3}")
print(f"Limite superior: {limite_superior}")
print(f"Máximo: {max(graus)}")


pto_outliers = 0 

for emp in graus:
  if emp>= limite_superior:
    pto_outliers+=1

print(f"Numero de Empresas Patio outliers (importantes quanto grau): {pto_outliers} ")

print()
numero_original_de_componentes =  nx.number_weakly_connected_components(G)
print(f"Número total de componentes conexas: {numero_original_de_componentes}")


#  Adicionando  coluna de grau de um node
df_pto['Grau'] = df_pto['CPF_CNPJ_Rem'].apply(lambda x: G.degree(x))


#  Filtrando os outliers do tipo patio

df_pto_outliers = df_pto[df_pto['Grau']>= limite_superior]
df_pto_outliers.loc[:, 'is_bridge_linkage'] = False


# Analisando  o numero de componentes que 
#  são obtidas ao remover os vertices pto 

components = []

print()
print("Analisando componentes dos possíveis pontos de articulação")
print("...")
for node in list(df_pto_outliers['CPF_CNPJ_Rem']):
    SG = nx.subgraph_view(G, filter_node= lambda x: x != node)
    components.append(nx.number_weakly_connected_components(SG))
print("Analisado")

df_pto_outliers['Conected_Components']= components
df_pto_outliers.loc[df_pto_outliers['Conected_Components'] > numero_original_de_componentes, 'is_bridge_linkage'] = True

print()
qtd_de_pontes_de_articulacao =  df_pto_outliers['is_bridge_linkage'].sum()
print(f"Das empresas importantes, quantas são ponts de  de articulação: {qtd_de_pontes_de_articulacao}")


