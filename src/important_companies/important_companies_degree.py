"""  
Analisa as empresas importantes quanto ao grau
Verifica se são pontos de articulação
"""
import pandas as pd
import networkx as nx
import numpy as np
from networkx.classes.function import path_weight
from tqdm import tqdm
from modules import  get_concessions, get_sink_nodes, get_timberflow
from data_cleaner import convert_id_to_str

#  Lendo os csvs
transportes_janeiro =  pd.read_csv('data/df_01.csv')
transportes_feveiro = pd.read_csv('data/df_02.csv')
transportes_marco = pd.read_csv('data/df_03.csv')
transportes_abril = pd.read_csv('data/df_04.csv')
transportes_maio = pd.read_csv('data/df_05.csv')
transportes_junho = pd.read_csv('data/df_06.csv')

transportes_julho = pd.read_csv('data/df_07.csv')
transportes_agosto = pd.read_csv('data/df_08.csv')
transportes_setembro = pd.read_csv('data/df_09.csv')
transportes_outubro= pd.read_csv('data/df_10.csv')
transportes_novembro = pd.read_csv('data/df_11.csv')
transportes_dezembro = pd.read_csv('data/df_12.csv')

tranporte_ano= pd.concat([transportes_janeiro,transportes_feveiro,transportes_marco,transportes_abril,transportes_maio, transportes_junho, transportes_julho, transportes_agosto, transportes_setembro, transportes_outubro, transportes_novembro, transportes_dezembro], ignore_index=True)



df_tran = tranporte_ano[['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes', 'Volume']]
df_tran= df_tran.groupby(['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes'])['Volume'].sum().reset_index()
df_tran = convert_id_to_str(df_tran) #normalizando os ids para string


#  Empresas do tipo Patio q_ue transportam para empresas do tipo pátio
df_pto = df_tran[(df_tran['TpRem'] == 'PTO_IBAMA') & (df_tran['TpDes'] == 'PTO_IBAMA')].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ'})
df_pto = df_pto.groupby('CPF_CNPJ')['Volume'].sum().reset_index()

# Dataframes com os nós do grafo
nodes = set(df_tran['CPF_CNPJ_Rem']).union(set(df_tran['CPF_CNPJ_Des']))
nodes_pto = set(df_pto['CPF_CNPJ'])

#  Criando grafo
G = nx.DiGraph()
G.add_nodes_from(nodes) # Adicionando vertices


# Cria as arestas com base nas transações e com peso = volume
edges = []
for row in df_tran.iterrows():
    # Ignora laços
    if str(row[1]['CPF_CNPJ_Rem']) != str(row[1]['CPF_CNPJ_Des']):
        edges.append((str(row[1]['CPF_CNPJ_Rem']), str(row[1]['CPF_CNPJ_Des']), {'Volume': row[1]['Volume']}))
G.add_edges_from(edges) #Adicionando arestas

# Dicionario para obter os graus de cada vertice (empresa) importante
emp_pto_degree = {}

for node in nodes_pto:
    emp_pto_degree[node]= G.degree(node)

#  Lista com os graus  dos vertices importantes
graus = list(emp_pto_degree.values())

# Criando o limite para determinar se uma empresa é importante
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
df_pto['Grau'] = df_pto['CPF_CNPJ'].apply(lambda x: G.degree(x))


#  Filtrando os outliers do tipo patio

df_pto_outliers = df_pto[df_pto['Grau']>= limite_superior]
df_pto_outliers.loc[:, 'is_bridge_linkage'] = False

components = []

print()
print("Analisando componentes dos possíveis pontos de articulação")
print("...")
for node in list(df_pto_outliers['CPF_CNPJ']):
    SG = nx.subgraph_view(G, filter_node= lambda x: x != node)
    components.append(nx.number_weakly_connected_components(SG))
print("Analisado")

df_pto_outliers['Conected_Components']= components
df_pto_outliers.loc[df_pto_outliers['Conected_Components'] > numero_original_de_componentes, 'is_bridge_linkage'] = True

print()
qtd_de_pontes_de_articulacao =  df_pto_outliers['is_bridge_linkage'].sum()
print(f"Das empresas importantes, quantas são pontos de  de articulação: {qtd_de_pontes_de_articulacao}")

#  Analisando componentes conexas com mais empresa importantes

# CNPJ/CPFS das empresas importantes
importante_nodes = list(df_pto_outliers['CPF_CNPJ'])

#  Componentes fracamente conexas
weakly_connected_components = list(nx.weakly_connected_components(G))


result = [
    set(component) & set(importante_nodes)
    for component in weakly_connected_components
    if len(set(component) & set(importante_nodes)) > 1
]

#  Componente fracamente conexas
num_components_with_important = len(result)

print(f"Numero de componentes conexas com mais de uma empresa importante: {num_components_with_important}")

print(f"Conjuntos de nós importantes em componentes fracamente conexas:")
for comp in result:
    print(f"Quantidade de empresas importante nessa componente fracamente conexa: {len(comp)}")
    print(f"Vertice importante nessa componente conexa: {comp}")
    print()
    

strongly_connected_components = list(nx.strongly_connected_components(G))

# Filtrar componentes com mais de um nó importante, mantendo apenas os nós importantes
result_strong  = [
    set(component) & set(importante_nodes)
    for component in strongly_connected_components
    if len(set(component) & set(importante_nodes)) > 1
]
print(f'Numero de componentes fortemente conexas com mais de uma empresa importante: {len(result)} ')
print(f"Conjuntos de nós importantes em componentes fortemente conexas:")

for comp in result_strong:
    print(f"Numero de vertices importantes nessa componente: {len(comp)}")
    print("Vertices importantes nessa componente:")
    print(comp)
    print()
    
print(30*"*")
# TODO v
#  Ver o fluxo das componentes conexas com mais vertices

