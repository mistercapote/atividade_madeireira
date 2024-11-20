import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from modules import *
import glob


# Guarda os dados dos csvs num DataFrame
# path = '..\\data'+
# df = pd.concat(map(pd.read_csv, glob.glob(path + "/*.csv")))
df = pd.concat(map(lambda f: pd.read_csv(f, low_memory=False), ['data/df_01.csv', 'data/df_02.csv','data/df_03.csv', 'data/df_04.csv', 'data/df_05.csv', 'data/df_06.csv']))

# Separa os dados das transações somando o volume das duplicadas
df_tran = df[['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes', 'Volume']]
df_tran = df_tran.groupby(['CPF_CNPJ_Rem', 'TpRem', 'CPF_CNPJ_Des', 'TpDes'])['Volume'].sum().reset_index()

df_nodes = df[['CPF_CNPJ_Rem', 'TpRem']].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ', 'TpRem': 'Tipo'})

# Ordena pelo tipo antes de remover as duplicatas para dar preferencia ao manejo
df_nodes = pd.concat([df_nodes, df[['CPF_CNPJ_Des', 'TpDes']].rename(columns={'CPF_CNPJ_Des': 'CPF_CNPJ', 'TpDes': 'Tipo'})]).sort_values(by=['Tipo']).drop_duplicates('CPF_CNPJ')
df_volume_analysis = pd.DataFrame(columns= ['CPF_CNPJ', 'Volume_Saida', 'Tamanho_Componente', 'Com_InFlow', 'Com_Out_Flow', 'Sem_InFlow', 'Sem_OutFlow'])

# Dicionario com CPF_CNPJ das empresas e seus respectivos tipos 
emps = {}
for i,node in df_nodes.iterrows():
    emps[node['CPF_CNPJ']] = node['Tipo']


# Cria o grafo direcionado com os vértices sendo os remetentes e destinatários 
nodes = set(df_tran['CPF_CNPJ_Rem']).union(set(df_tran['CPF_CNPJ_Des']))
G = nx.DiGraph()
G.add_nodes_from(nodes)

# Cria as arestas com base nas transações e com peso = volume
edges = []
for row in df_tran.iterrows():
    # Ignora laços
    if int(row[1]['CPF_CNPJ_Rem']) != int(row[1]['CPF_CNPJ_Des']):
        edges.append((int(row[1]['CPF_CNPJ_Rem']), int(row[1]['CPF_CNPJ_Des']), {'Volume': row[1]['Volume']}))
G.add_edges_from(edges)


# DataFrame com as transações apenas entre dois pátios
df_pto = df_tran[(df_tran['TpRem'] == 'PTO_IBAMA') & (df_tran['TpDes'] == 'PTO_IBAMA')].rename(columns={'CPF_CNPJ_Rem': 'CPF_CNPJ'})
df_pto = df_pto.groupby('CPF_CNPJ')['Volume'].sum().reset_index()


# Dados das transacoes
median = df_pto['Volume'].median()
q1 = df_pto['Volume'].quantile(0.25)
q3 = df_pto['Volume'].quantile(0.75)
ls = median + 1.5*(q3-q1)

# DataFrame com apenas as empresas importantes de acordo com o volume
df_pto = df_pto[df_pto['Volume'] > ls]

# Verifica a quantidade de componentes conexas antes e depois de retirar os vertices
print(nx.number_weakly_connected_components(G))
components = []
for node in list(df_pto['CPF_CNPJ']):
    SG = nx.subgraph_view(G, filter_node= lambda x: x != node)
    components.append(nx.number_weakly_connected_components(SG))

df_pto['Conected_Components'] = components


# Constrói árvores com a raiz sendo o manejo
manejos = set(df_nodes[df_nodes['Tipo'] == 'MANEJO']['CPF_CNPJ'])
finais = set(df_nodes[df_nodes['Tipo'] == 'FINAL']['CPF_CNPJ'])
all_important_patios = set(df_pto['CPF_CNPJ'])
aux_valid_patios = set()
valid_patios = set()

# Verifica 
for each_manejo in manejos:
    T = nx.bfs_tree(G, each_manejo)
    if finais.intersection(set(T.nodes())) != set():
        # Salva os pátios que são conectados a um manejo
        aux_valid_patios.update(all_important_patios.intersection(set(T.nodes())))

# Atualiza o dataframe com o CPF_CNPJ e o Volume de Saida das empresas importantes
for each_valid_patio in aux_valid_patios:
    df_volume_analysis.loc[len(df_volume_analysis), 'CPF_CNPJ'] = each_valid_patio

dict_filter = df_pto[['CPF_CNPJ','Volume']].set_index('CPF_CNPJ')['Volume'].to_dict()
df_volume_analysis['Volume_Saida'] = df_volume_analysis['CPF_CNPJ'].map(dict_filter)

# Filtra quais pátios chegam a um final
for each_patio in aux_valid_patios:
    T = nx.bfs_tree(G, each_patio)
    if finais.intersection(set(T.nodes())) != set():
        # Salva os pátios que são conectados a um final
        valid_patios.update(aux_valid_patios.intersection(set(T.nodes())))


aux = nx.weakly_connected_components(G)
emps_components = {}
list_components = []
components = []
cont = 0

# Verifica quais componentes fortemente conexas possuem mais de um vértice
for each_component in aux:
    if len(each_component) > 1:
        cont += 1

        # Salva os patios e suas respectivas componentes
        for patio in valid_patios:
            if patio in each_component:
                emps_components[patio] = each_component
                dict_filter[patio] = len(each_component)
                if each_component not in components:
                    components.append(each_component)

df_volume_analysis['Tamanho_Componente'] = df_volume_analysis['CPF_CNPJ'].map(dict_filter).astype(dtype='int32')
print(df_volume_analysis[df_volume_analysis['Tamanho_Componente'] == 202])

# Verifica o fluxo nas componentes conexas
for index, component in enumerate(components):
    SG = nx.subgraph_view(G, filter_node= lambda x: x in component)
    aux_emp = {x: emps[x] for x in component}
    total_in = total_out = 0

    try: 
        print(len(component))
        total_in, total_out = get_timberflow(SG, aux_emp)
    except ZeroDivisionError:
        print("Sem entrada")

    print("#"*40)
    
    # Verifica o fluxo das componentes retirando os patios
    for each_patio, each_component in emps_components.items():
        if each_component == component:
            dict_filter[each_patio] = [total_in, total_out]
            total_in_sem = total_out_sem = 0
            each_component.remove(each_patio)
            SG = nx.subgraph_view(G, filter_node= lambda x: x in each_component)
            aux_emp = {x: emps[x] for x in each_component}

            try: 
                print('Pátio: ', each_patio)
                total_in_sem, total_out_sem = get_timberflow(SG, aux_emp)
            except ZeroDivisionError:
                print("Sem entrada")
            
            
            dict_filter[each_patio].extend([total_in_sem, total_out_sem])

print(dict_filter)

# Atualiza o DataFrame para a analise com os dados do fluxo
df_volume_analysis['Com_InFlow'] = df_volume_analysis['CPF_CNPJ'].map(lambda x: dict_filter[x][0])
df_volume_analysis['Com_Out_Flow'] = df_volume_analysis['CPF_CNPJ'].map(lambda x: dict_filter[x][1])
df_volume_analysis['Sem_InFlow'] = df_volume_analysis['CPF_CNPJ'].map(lambda x: dict_filter[x][2])
df_volume_analysis['Sem_OutFlow'] = df_volume_analysis['CPF_CNPJ'].map(lambda x: dict_filter[x][3])

df_volume_analysis.to_csv('VolumeAnalysis.csv')