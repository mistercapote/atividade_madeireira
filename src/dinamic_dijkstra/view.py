import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Carregar o DataFrame e corrigir formatos
df = pd.read_csv('cumulative_paths.csv')
df["path"] = df["path"].str.split(" <- ")
df['period'] = pd.to_datetime(df['period'], format='%Y-%m')
df = df.sort_values(by=['period', 'path'], ascending=[True, True], key=lambda x: x.apply(lambda y: y[-1] if isinstance(y, list) else None))

# Construir os grafos para cada período
period_groups = df.groupby('period')
df_graphs = pd.DataFrame(columns=["period", "graph"])
for period, group in period_groups:
    G = nx.DiGraph() 
    for _, row in group.iterrows():
        path = row['path']
        for i in range(len(path) - 1):
            if i == len(path) - 2:
                G.add_edge(path[i], path[i + 1], weight=row['weight'])
            else:
                G.add_edge(path[i], path[i + 1])
    df_graphs.loc[len(df_graphs)] = [period, G]

# Função para calcular a altura de um nó
def calculate_node_height(G, node):
    lengths = nx.single_source_shortest_path_length(G.reverse(), node)
    return max(lengths.values()) if lengths else 0

# Função para desenhar o grafo correspondente ao período
def update_graph(val):
    global ax
    ax.clear()
    idx = int(slider.val)
    row = df_graphs.iloc[idx] 
    graph = row["graph"]
    
    # Agrupar nós por altura
    height_groups = {}
    for node in graph.nodes:
        height = calculate_node_height(graph, node)
        if height not in height_groups:
            height_groups[height] = []
        height_groups[height].append(node)
    
    # Ajustar a posição dos nós: distribua os nós de mesma altura igualmente no eixo y
    pos = {}
    for height, nodes in height_groups.items():
        xpos = height
        ypos = height / len(nodes)
        for node in nodes:
            pos[node] = (xpos, ypos)
            ypos += height / len(nodes)
    
    # Definir cores dos nós
    node_colors = []
    for node in graph.nodes:
        if node in [path[0] for path in df["path"]]: node_colors.append('blue') 
        elif node in [path[-1] for path in df["path"]]: node_colors.append('orange')
        else: node_colors.append('gray')

    # Desenho do grafo com cores ajustadas
    nx.draw(graph, pos, ax=ax, with_labels=False, node_color=node_colors, node_size=600)
    for node, (x, y) in pos.items():
        ax.text(x, y - 0.2, node, fontsize=12, ha='center', va='center', color='black')

    # Adicionar pesos das arestas
    for _, v, data in graph.edges(data=True):
        weight = data.get('weight', "")  # Peso padrão é vazio
        x, y = pos[v]
        x += 0.3
        ax.text(x, y, f'{weight}', fontsize=15, ha='left', va='center', color='black')
      
    ax.set_title(f"Caminhos em {row['period'].strftime('%m/%Y')}", fontsize=20)
    slider.valtext.set_text(f'{df_graphs["period"].iloc[idx].strftime("%m/%Y")}')
    fig.canvas.draw_idle()

# Configurando a visualização inicial
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25, right=0.85)

# Criando o slider
slider = Slider(
    plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow'), 
    "Período", 
    0, 
    len(df_graphs) - 1, 
    valinit=0, 
    valstep=1
)

# Conectando o slider à função de atualização
update_graph(slider.val)
slider.on_changed(update_graph)

plt.show()


