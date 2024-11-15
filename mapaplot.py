import pandas as pd
import folium


df = pd.read_csv('/home/ximena/Desktop/XiemenaPaperReview/data/mandioqueiro.csv', low_memory=False, dtype={'CPF_CNPJ_Rem': str, 'CPF_CNPJ_Des': str})


nodos = {}


for _, row in df.iterrows():
    coord_origem = (row['LatOrigem'], row['LongOrigem'])
    coord_destino = (row['LatDestino'], row['LongDestino'])

    id_origem = row['CPF_CNPJ_Rem']
    id_destino = row['CPF_CNPJ_Des']


    if pd.notnull(coord_origem[0]) and pd.notnull(coord_origem[1]):
        if id_origem not in nodos:
            nodos[id_origem] = {
                'latitude': coord_origem[0],
                'longitude': coord_origem[1],
                'type': row['TpRem']
            }

    if pd.notnull(coord_destino[0]) and pd.notnull(coord_destino[1]):
        if id_destino not in nodos:
            nodos[id_destino] = {
                'latitude': coord_destino[0],
                'longitude': coord_destino[1],
                'type': row['TpDes']
            }


df_nodos = pd.DataFrame(nodos.values())


mapa = folium.Map(location=[df_nodos['latitude'].mean(), df_nodos['longitude'].mean()], zoom_start=5)


for _, row in df_nodos.iterrows():
    if row['type'] == 'MANEJO':
        color = 'red'
    elif row['type'] == 'PTO_IBAMA':
        color = 'blue'
    elif row['type'] == 'FINAL':
        color = 'green'
    else:
        color = 'gray'  
        
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=1,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7
    ).add_to(mapa)


mapa.save('mapa_nodos.html')
