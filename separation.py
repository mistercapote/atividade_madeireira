import pandas as pd


df = pd.read_csv('/home/ximena/Desktop/XiemenaPaperReview/data/mandioqueiro.csv', low_memory=False, dtype={'CPF_CNPJ_Rem': str, 'CPF_CNPJ_Des': str})

transportes = []
nodos = {}

for _, row in df.iterrows():
    coord_origem = (row['LatOrigem'], row['LongOrigem'])
    coord_destino = (row['LatDestino'], row['LongDestino'])

    id_origem = row['CPF_CNPJ_Rem']
    id_destino = row['CPF_CNPJ_Des']
    volume = row['Volume']
    producto = row['Produto']
    fecha = row['datetimeDtEmissao']
    

    if row['Status'] == 'Recebido':
        transportes.append({
            'node_src': id_origem,
            'node_dest': id_destino,
            'vol': volume,
            'id_product': producto,
            'date': fecha
        })


        if id_origem not in nodos:
            nodos[id_origem] = {
                'id_emp': id_origem,
                'latitude': coord_origem[0],
                'longitude': coord_origem[1],
                'type': row['TpRem']
            }


        if id_destino not in nodos:
            nodos[id_destino] = {
                'id_emp': id_destino,
                'latitude': coord_destino[0],
                'longitude': coord_destino[1],
                'type': row['TpDes']
            }
    elif row['NomeDestino'] == 'CONSUMIDOR FINAL':
        transportes.append({
            'node_src': id_origem,
            'node_dest': id_destino,
            'vol': volume,
            'id_product': producto,
            'date': fecha
        })


        if id_origem not in nodos:
            nodos[id_origem] = {
                'id_emp': id_origem,
                'latitude': coord_origem[0],
                'longitude': coord_origem[1],
                'type': row['TpRem']
            }


        if id_destino not in nodos:
            nodos[id_destino] = {
                'id_emp': id_destino,
                'latitude': coord_destino[0],
                'longitude': coord_destino[1],
                'type': row['TpDes']
            }


df_transportes = pd.DataFrame(transportes)
df_nodos = pd.DataFrame(nodos.values())


df_transportes.to_csv('/home/ximena/Desktop/XiemenaPaperReview/Main/transports.csv', index=False)
df_nodos.to_csv('/home/ximena/Desktop/XiemenaPaperReview/Main/nodes.csv', index=False)
