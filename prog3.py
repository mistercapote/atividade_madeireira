import pandas as pd
import networkx as nx
from networkx.classes.function import path_weight
from tqdm import tqdm
from datetime import datetime

# Leer los archivos CSV
transports = pd.read_csv('/home/ximena/Desktop/XiemenaPaperReview/Main/transports.csv', low_memory=False)
emps = pd.read_csv('Main/nodes.csv', low_memory=False)
print("Datos Leídos")


transports['date'] = pd.to_datetime(transports['date'], errors='coerce') 


emp_type = {node['id_emp']: node['type'] for _, node in emps.iterrows()}


source = '14159781000176'
k = 3  

def create_graph(transports, product_filter=None):
    graph = {}
    for _, transport in tqdm(transports.iterrows(), total=len(transports)):
        id_emp_orig = transport['node_src']
        id_emp_dest = transport['node_dest']
        volume = transport['vol']

        if graph.get(id_emp_orig) is None:
            graph[id_emp_orig] = {id_emp_dest: {'weight': -volume}}
        else:
            if graph[id_emp_orig].get(id_emp_dest) is None:
                graph[id_emp_orig][id_emp_dest] = {'weight': -volume}
            else:
                graph[id_emp_orig][id_emp_dest]['weight'] -= volume

    return nx.DiGraph(graph)


def dijkstra(G, source, emp_type, k):
    length, paths = nx.single_source_dijkstra(G, source)
    target_weights = {}

    for target, path in paths.items():
        if emp_type.get(target) == 'MANEJO':
            target_weights[target] = path_weight(G, path, weight='weight')

    target_ordered = sorted(target_weights.items(), key=lambda x: x[1])[:k]
    return paths, target_ordered


def eppistein(G, source, target, k):
    paths = []
    for path in nx.shortest_simple_paths(G, source, target, weight='weight'):
        if len(paths) >= k:
            break
        paths.append((path, path_weight(G, path, weight='weight')))
    return paths

def eppistein_graph(G, source, target_weight, k, dijkstra_paths):
    paths = []
    for target, weight in target_weight:
        paths += eppistein(G, source, target, k)
    limit = k if len(paths) >= k else len(paths)
    return sorted(paths, key=lambda x: x[1])[:limit]

def original_path_cost(paths, original_graph):
    for i, (path, weight) in enumerate(paths):
        paths[i] = (path, -1.0 * path_weight(original_graph, path, weight='weight'))
    return paths


transports['year_month'] = transports['date'].dt.to_period('M') 
unique_months = sorted(transports['year_month'].unique())
cumulative_data = pd.DataFrame()  


monthly_paths = []


for period in unique_months:
    print(f"\nProcessing period: {period}")
    
    # Filtrar datos hasta el mes actual para un cálculo acumulativo
    period_data = transports[transports['year_month'] <= period]      
    
    # Crear el grafo acumulativo hasta el mes actual
    graph = create_graph(period_data)
    graph_reversed = graph.reverse().copy()
    G = graph_reversed.copy()

    # Ajustar pesos negativos para maximizar el peso de las rutas
    min_weight = min(G.edges(data='weight'), key=lambda x: x[2])[2]
    attrs = {edge: {"weight": G.edges[edge]['weight'] - min_weight} for edge in G.edges}
    nx.set_edge_attributes(G, attrs)

    # Encontrar el camino acumulativo hacia el nodo final
    try:
        paths, target_ordered = dijkstra(G, source, emp_type, k)
        secondary_paths = eppistein_graph(G, source, target_ordered, k, paths)
        secondary_paths = original_path_cost(secondary_paths, graph_reversed)
        
        # Guardar el camino para el mes en formato acumulativo
        for path, weight in secondary_paths:
            monthly_paths.append({
                "period": period,
                "path": " <- ".join(map(str, path)),
                "weight": round(weight, 2)
            })

    except nx.NetworkXNoPath:
        print(f"No path found for period {period}")

cumulative_paths_df = pd.DataFrame(monthly_paths)
cumulative_paths_df.to_csv("cumulative_paths.csv", index=False)
print("Caminos acumulativos guardados en cumulative_paths.csv")
