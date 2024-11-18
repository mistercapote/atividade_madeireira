import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime
from networkx.classes.function import path_weight
import plotly.graph_objects as go
import plotly.express as px

# Función para crear el grafo a partir de los datos de transporte
def create_graph(transports):
    graph = {}
    for i, transport in tqdm(transports.iterrows()):
        id_emp_orig = transport['node_src']
        id_emp_dest = transport['node_dest']
        volume = transport['vol']

        if graph.get(id_emp_orig) is None:
            graph[id_emp_orig] = {id_emp_dest: {'weight': volume}}
        else:
            if graph[id_emp_orig].get(id_emp_dest) is None:
                graph[id_emp_orig][id_emp_dest] = {'weight': volume}
            else:
                graph[id_emp_orig][id_emp_dest]['weight'] += volume

    for source, targets in graph.items():
        for target, volume in targets.items():
            graph[source][target]['weight'] = -1 * volume['weight']

    return nx.DiGraph(graph)

# Leer los archivos CSV
#transports = pd.read_csv('transports.csv')
transports = pd.read_csv('edges.csv', low_memory=False)
#emps = pd.read_csv('nodes.csv')
emps = pd.read_csv('nodes.csv', low_memory=False)
print("Datos Leidos")
# Crear diccionario emp_type
emp_type = {}
for i, node in emps.iterrows():
    emp_type[node['id_emp']] = node['type']

# Crear el grafo
graph = create_graph(transports)
G_orig_weight = graph.copy()

# Función para obtener concesiones
def get_concessions(list_nodes, emp_type):
    count = 0
    for node in list_nodes:
        if emp_type.get(node) == 'MANEJO':  # Usar get() para evitar KeyError
            count += 1
    return count

# Función para imprimir métricas del grafo
def print_graph_metrics(graph, emp_type):
    g_aux = G_orig_weight.to_undirected()
    components_len = []
    for item in nx.connected_components(g_aux):
        components_len.append((len(item), item))

    print(f'Total Graph: {graph}')
    print(f'Number of components: {len(components_len)}')
    print(f'Number of concessions: {get_concessions(graph.nodes(), emp_type)}')

    print('Components with more than 1000 nodes:')
    for c in components_len:
        if c[0] > 1000:
            subg = graph.subgraph(c[1])
            print(f'Subgraph: {subg}')
            print(f'Number of concessions: {get_concessions(subg.nodes(), emp_type)}')

# Mostrar métricas del grafo
print_graph_metrics(G_orig_weight, emp_type)

# Función para obtener nodos finales
def get_sink_nodes(graph, emp_type):
    nodes = {}
    for node in graph.nodes():
        if emp_type.get(node) == 'FINAL':
            nodes[node] = 1
            continue
        not_sink = False
        for edge in graph.edges(node):
            if emp_type.get(edge[1]) != 'FINAL':
                not_sink = True
        if not not_sink:
            nodes[node] = 1
    return nodes

# Función para calcular el flujo de madera
def get_timberflow(graph, emp_type):
    sink_nodes = get_sink_nodes(graph, emp_type)
    total_in = 0
    total_out = 0

    for edge in graph.edges():
        if emp_type.get(edge[0]) == 'MANEJO':
            total_in += -path_weight(graph, [edge[0], edge[1]], weight='weight')
        elif edge[1] in sink_nodes:
            total_out += -path_weight(graph, [edge[0], edge[1]], weight='weight')
    
    
    print(f'Inflow Vol(m3): {total_in} \nOut Vol(m3): {total_out} \n In / out :  {total_out / total_in}')



# Calcular el flujo de madera
get_timberflow(G_orig_weight, emp_type)


# Implementación de Dijkstra
def dijkstra(G, source, emp_type, k):
    length, paths = nx.single_source_dijkstra(G, source)
    target_weights = {}

    for target, path in paths.items():
        if emp_type.get(target) == 'MANEJO':
            target_weights[target] = path_weight(G, path, weight='weight')

    target_ordered = sorted(target_weights.items(), key=lambda x: x[1])[:k]
    return paths, target_ordered

# Implementación de Eppstein
def eppistein(G, source, target, k):
    paths = []
    for path in nx.shortest_simple_paths(G, source, target, weight='weight'):
        if len(paths) >= k:
            break
        paths.append((path, path_weight(G, path, weight='weight')))
    return paths

def eppistein_graph(G, source, target_weight, k, dijkstra_paths):
    paths = []
    for i, (target, weight) in enumerate(target_weight):
        paths += eppistein(G, source, target, k)
    limit = k if len(paths) >= k else len(paths)
    return sorted(paths, key=lambda x: x[1])[:limit]

def original_path_cost(paths, original_graph):
    for i, (path, weight) in enumerate(paths):
        paths[i] = (path, -1.0 * path_weight(original_graph, path, weight='weight'))
    return paths

# Invertir el grafo para calcular rutas inversas
graph_reversed = graph.reverse().copy()
G = graph_reversed.copy()

# Ajustar pesos negativos para maximizar el peso de las rutas
min_weight = min(G.edges(data='weight'), key=lambda x: x[2])[2]
attrs = {}
for edge in G.edges:
    attrs[edge] = G.edges[edge]
    attrs[edge]['weight'] += -min_weight
nx.set_edge_attributes(G, attrs)

###################################################### ESTO LE METI #########################################################################################
# def nodos_finales_prometedores(graph, emp_type):
#     # 1. Filtrar los nodos que son 'FINAL'
#     nodos_finales = [node for node in graph.nodes if emp_type.get(node) == 'FINAL']
    
#     # 2. Calcular el flujo de entrada a cada nodo final
#     flujo_entrada = {}
    
#     for nodo_final in nodos_finales:
#         total_in = 0
#         for pred in graph.predecessors(nodo_final):  # Predecessors son los nodos que apuntan al nodo_final
#             total_in += -graph[pred][nodo_final]['weight']  # Sumamos el peso (volumen) de cada arista que llega al nodo final
        
#         flujo_entrada[nodo_final] = total_in

#     # 3. Ordenar los nodos finales por el flujo de entrada (de mayor a menor)
#     nodos_finales_ordenados = sorted(flujo_entrada.items(), key=lambda x: x[1], reverse=True)

#     return nodos_finales_ordenados

# # Encontrar los nodos finales más prometedores
# nodos_finales_ordenados = nodos_finales_prometedores(G_orig_weight, emp_type)

# # Seleccionar el mejor nodo (el que tiene mayor flujo de entrada)
# mnodo = nodos_finales_ordenados[0][0] if nodos_finales_ordenados else None  # Asegurar que la lista no esté vacía

# # Imprimir el mejor nodo
# print(f"El mejor nodo final es: {mnodo}")



#################################################################################################################

def nodos_con_mayor_proporcion_y_salida(graph, emp_type, n):
    # 1. Filtrar los nodos que tienen tipo que empiezan con 'PTO_'
    nodos_pto = [node for node in graph.nodes if emp_type.get(node, '').startswith('PTO_')]
    
    if not nodos_pto:
        print("No se encontraron nodos con tipo que empieza con 'PTO_'")
        return [], []

    print(f"Se encontraron {len(nodos_pto)} nodos con tipo 'PTO_'")

    proporciones = []
    nodos_salida_mayor_entrada_cero = []

    # 2. Para cada nodo, calcular la división entre pesos de aristas que salen y las que entran
    for nodo in nodos_pto:
        total_out = 0
        total_in = 0

        # Calcular el total de pesos de aristas que salen
        for succ in graph.successors(nodo):
            total_out += graph[nodo][succ]['weight']

        # Calcular el total de pesos de aristas que entran
        for pred in graph.predecessors(nodo):
            total_in += graph[pred][nodo]['weight']

        # Verificar si el nodo tiene flujo de entrada igual a 0 y salida mayor que 0
        if total_in == 0 and total_out > 0:
            nodos_salida_mayor_entrada_cero.append((nodo, total_out))
        
        # Calcular la proporción considerando entrada negativa o positiva
        if total_in != 0:  # Se considera entrada negativa o positiva
            proporcion = total_out / total_in
            proporciones.append((nodo, proporcion))

    # 3. Ordenar los nodos por la proporción (de mayor a menor)
    nodos_ordenados_por_proporcion = sorted(proporciones, key=lambda x: x[1], reverse=True)

    # 4. Ordenar los nodos con salida mayor que 0 y entrada igual a 0 por su salida (de mayor a menor)
    nodos_ordenados_por_salida = sorted(nodos_salida_mayor_entrada_cero, key=lambda x: x[1], reverse=True)

    # 5. Devolver los n nodos con la mayor proporción y los n nodos con mayor salida
    return nodos_ordenados_por_proporcion[:n], nodos_ordenados_por_salida[:n]

# Ejemplo de uso:
n = 5  # El número de nodos con mayores proporciones que quieres obtener
nodos_mayor_proporcion, nodos_mayor_salida = nodos_con_mayor_proporcion_y_salida(G_orig_weight, emp_type, n)

# Imprimir los nodos con mayores proporciones
print("Nodos con mayores proporciones (salida/entrada):")
for nodo, proporcion in nodos_mayor_proporcion:
    print(f"Nodo: {nodo}, Proporción (salida/entrada): {proporcion}")

# Imprimir los nodos con salida mayor que 0 y entrada igual a 0
print("Nodos con salida mayor a 0 y entrada igual a 0:")
for nodo, salida in nodos_mayor_salida:
    print(f"Nodo: {nodo}, Salida: {salida}")

# El mejor nodo (con mayor proporción)
mnodo=nodos_mayor_proporcion[0][0] if nodos_mayor_proporcion else nodos_mayor_salida[0][0] if nodos_mayor_salida else None

# Imprimir el mejor nodo
print(f"El mejor nodo final es: {mnodo}")


###################################################### ESTO LE METI ##########################################################################################

# Parámetros
k = 3

# Encontrar los caminos más probables
paths, target_ordered = dijkstra(G, mnodo, emp_type, k)
secondary_paths = eppistein_graph(G, mnodo, target_ordered, k, paths)

# Mostrar caminos con pesos corregidos
secondary_paths = original_path_cost(secondary_paths, graph_reversed)
for path, weight in secondary_paths:
    print(f"(FINAL) {' <- '.join(map(str, path))} (SOURCE) - Weight: {round(weight, 2)} M3")

# Filtrar nodos correspondientes a los caminos
emps_filtered = emps[emps['id_emp'].isin(set([node for (path, weight) in secondary_paths for node in path]))].copy()
emps_filtered['size'] = 10

# Graficar los caminos en el mapa
for path, weight in secondary_paths:
    fig = px.scatter_mapbox(
        emps_filtered[emps_filtered['id_emp'].isin(path)],
        lat="latitude",
        lon="longitude",
        zoom=8,
        mapbox_style='open-street-map',
        color='type',
        size='size',
        size_max=15,
        width=1000,
        height=500
    )
    fig.show()

print("Desde aqui -------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
# Leer el archivo nodes.csv
#emps = pd.read_csv('./nodes.csv')

# Mostrar las primeras filas del dataframe
print(emps.head())

# Filtrar nodos presentes en los caminos secundarios
# Extraemos los nodos de los caminos (secondary_paths)
nodos_en_caminos = set([node for (path, weight) in secondary_paths for node in path])

# Filtrar los nodos del dataframe emps que están presentes en los caminos
emps_filtered = emps[emps['id_emp'].isin(nodos_en_caminos)].copy()

# Añadir una columna 'size' para controlar el tamaño de los nodos en el gráfico
emps_filtered['size'] = 10

# Mostrar las primeras filas del dataframe filtrado
print(emps_filtered)

# Visualizar los caminos en un mapa interactivo
for path, weight in secondary_paths:
    # Filtrar los nodos del camino actual
    nodos_camino = emps_filtered[emps_filtered['id_emp'].isin(path)]
    
    # Crear la visualización del mapa con Plotly
    fig = px.scatter_mapbox(
        nodos_camino, 
        lat="latitude", 
        lon="longitude", 
        zoom=8, 
        mapbox_style='open-street-map', 
        color='type', 
        size='size', 
        size_max=15, 
        width=1000, 
        height=500
    )

    # Mostrar el gráfico
    fig.show()
