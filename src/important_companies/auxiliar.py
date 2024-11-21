import networkx as nx
import matplotlib.pyplot as plt


nodes = ['Manejo', 'Pátio1', 'Pátio2', 'Pátio3', 'Final']
edges = [('Manejo', 'Pátio1'), ('Manejo', 'Pátio2'), ('Manejo', 'Pátio3'), ('Pátio1', 'Final'), ('Pátio2', 'Final')]

G = nx.DiGraph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

pos_nodes = {
    'Manejo': (1,4), 
    'Pátio1': (3,6), 
    'Pátio2': (3,4), 
    'Pátio3': (3,2), 
    'Final': (5,5)
}

pos_edges = {
    'Manejo': (0.95,4), 
    'Pátio1': (2.95,6), 
    'Pátio2': (2.95,4), 
    'Pátio3': (2.95,2), 
    'Final': (4.95,5)
}

pos_labels = {
    'Manejo': (1,3.6), 
    'Pátio1': (3,5.6), 
    'Pátio2': (3,3.6), 
    'Pátio3': (3,1.6), 
    'Final': (5,4.6)
}

options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.9}
nx.draw_networkx_nodes(G, pos_nodes, nodelist=['Manejo'], node_color="tab:blue", **options)
nx.draw_networkx_nodes(G, pos_nodes, nodelist=['Pátio1', 'Pátio2', 'Pátio3'], node_color="tab:gray", **options)
nx.draw_networkx_nodes(G, pos_nodes, nodelist=['Final'], node_color="tab:orange", **options)

nx.draw_networkx_edges(G, pos_edges, edgelist=edges, width=1.0, alpha=0.5)

labels = {}
labels['Manejo'] = r"Manejo"
labels['Pátio1'] = r"Pátio1"
labels['Pátio2'] = r"Pátio2"
labels['Pátio3'] = r"Pátio3"
labels['Final'] = r"Final"
nx.draw_networkx_labels(G, pos_labels, labels, font_size=15, font_color="black")

plt.tight_layout()
plt.axis("off")
plt.show()