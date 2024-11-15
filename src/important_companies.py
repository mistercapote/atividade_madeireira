import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from networkx.classes.function import path_weight
from tqdm import tqdm


def create_graph(transports):
    graph = {}

    # Creating the graph with the list of transports
    for i,transport in tqdm(transports.iterrows()):
        id_emp_orig = transport['node_src']
        id_emp_dest = transport['node_dest']

        volume = transport['vol']

        # Graph is a dict (source) -> (destination, weight)
        if graph.get(id_emp_orig) is None:
            # if source is not in the graph we need to map it as source to the destination
            graph[id_emp_orig] = {id_emp_dest: {'weight': volume }}
        else:
            # if source is already in the graph
            # 1. new destination from that source: create the edge
            # 2. source already mapped to destination: increase the volume in that edge
            if graph[id_emp_orig].get(id_emp_dest) is None:
                graph[id_emp_orig][id_emp_dest] = {'weight': volume }
            else:
                graph[id_emp_orig][id_emp_dest]['weight'] += volume

    # In this context we want to maximize paths over the volume
    # Since most functions minimizes over the weight of the edges,
    # we need to invert the relation
    for source, targets in graph.items():
        for target, volume in targets.items():
            graph[source][target]['weight'] = -1 * volume['weight']

    return nx.DiGraph(graph)

# transportes_junho = pd.read_csv('../data/df_06.csv')
transportes_julho = pd.read_csv('data/df_07.csv')
transportes_agosto = pd.read_csv('data/df_08.csv')
transportes_setembro = pd.read_csv('data/df_09.csv')
transportes_outubro= pd.read_csv('data/df_10.csv')
transportes_novembro = pd.read_csv('data/df_11.csv')
transportes_dezembro = pd.read_csv('data/df_12.csv')

transporte_primeiro_semestre= pd.concat([transportes_julho, transportes_agosto, transportes_setembro, transportes_outubro, transportes_novembro, transportes_dezembro], ignore_index=True)

rem_df = transporte_primeiro_semestre[['CPF_CNPJ_Rem', 'TpRem']].rename(columns={'CPF_CNPJ_Rem': 'CNPJ_CPF', 'TpRem': 'type'})
rem_df['source'] = 'Remetente'

# Criar DataFrame para CPF_CNPJ_Des e TpDes
des_df = transporte_primeiro_semestre[['CPF_CNPJ_Des', 'TpDes']].rename(columns={'CPF_CNPJ_Des': 'CNPJ_CPF', 'TpDes': 'type'})
des_df['source'] = 'Destinatário'

# Concatenar ambos os DataFrames
node_df= pd.concat([rem_df, des_df], ignore_index=True)
node_df.drop_duplicates('CNPJ_CPF')

# reading nodes and creating a dict for easy use

emp_type = {}

for i,node in node_df.iterrows():
  emp_type[node['CNPJ_CPF']] = node['type']
  
arestas = transporte_primeiro_semestre[['CPF_CNPJ_Rem', 'CPF_CNPJ_Des', 'Volume']].rename(columns={'CPF_CNPJ_Rem': 'node_src', 'CPF_CNPJ_Des': 'node_dest', 'Volume': 'vol'})

#  Removendo loops
arestas_1 = arestas[arestas['node_dest']!=arestas['node_src']]

graph = create_graph(arestas_1)


def get_concessions(list_nodes,emp_type): 
  # As concessões são todas emps marcadas como MANEJO,1
  # (fonte legal e extratores de madeira)

  count = 0
  for node in list_nodes:
    if emp_type[node] == 'MANEJO':
      count+=1

  return count

G_orig_weight = graph.copy()

def print_graph_metrics(graph, emp_type):
  # Print overall graph metrics

  g_aux = G_orig_weight.to_undirected()

  # Number of connected components in the graph
  components_len = []
  for item in nx.connected_components(g_aux):
    components_len.append((len(item),item))

  print(f'Total Graph: {graph}')
  print(f'Number of components: {len(components_len)}')
  print(f'Number of concessions: {get_concessions(graph.nodes(),emp_type)}')

  print()
  print()
  print('Components with more than 1000 nodes')
  for c in components_len:
    if c[0] > 1000:
      subg = graph.subgraph(c[1])

      print(f'Subgraph: {subg}')
      print(f'Number of concessions: {get_concessions(subg.nodes(),emp_type)}')
      print()
      print()
      
print_graph_metrics(G_orig_weight, emp_type)

nodes_manejo = [chave for chave, valor in emp_type.items() if valor == "MANEJO"]

graus_manejo = {}

for node in nodes_manejo:
    grau = graph.degree(node)
    graus_manejo[node] = grau

        
print(f"Quantidade de vertices do tipo manejo: {len(nodes_manejo)}")

print(f"Grau minimo: {min(graus_manejo.values())}")
print(f"Grau Máximo: {max(graus_manejo.values())}")

graus_num = list(graus_manejo.values())
print(f"Grau:    {graus_num}")
q1 = np.quantile(graus_num, 0.25)  # Primeiro quartil (25%)
q2 = np.quantile(graus_num, 0.5)   # Segundo quartil (50%, ou mediana)
q3 = np.quantile(graus_num, 0.75)  # Terceiro quartil (75%)
interquartil = q3-q1
limite_superior = q2 + 1.5*interquartil
print(f"Q1 (25%): {q1}")
print(f"Q2 (50% - Mediana): {q2}")
print(f"Q3 (75%): {q3}")
print(f"Limite superior: {limite_superior}")

#  Numeros de empresas outliers
manejos_outliers = 0 

for emp in graus_num:
  if emp>= limite_superior:
    manejos_outliers+=1

print(f"Numero de Empresas outliers (importantes quanto grau: {manejos_outliers} ")





