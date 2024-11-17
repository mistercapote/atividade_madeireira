import pandas as pd

df1 = pd.read_csv("data/df_01.csv", low_memory=False)


origem = df1[["CPF_CNPJ_Rem", "LatOrigem", "LongOrigem", "TpRem"]].rename(
    columns={
    'CPF_CNPJ_Rem': 'id_emp', 
    'LatOrigem': 'latitude', 
    'LongOrigem': 'longitude', 
    'TpRem': 'type'
})
destino = df1[["CPF_CNPJ_Des", "LatDestino", "LongDestino", "TpDes"]].rename(
    columns={
    'CPF_CNPJ_Des': 'id_emp', 
    'LatDestino': 'latitude', 
    'LongDestino': 'longitude', 
    'TpDes': 'type'
})
nodes_jan = pd.concat([origem, destino], ignore_index=True)
nodes_jan.drop_duplicates("id_emp", inplace=True)
nodes_jan.to_csv("data/nodes_jan.csv", index=False)

edges_jan = df1[["CPF_CNPJ_Rem", "CPF_CNPJ_Des", "Produto", "Volume", "DtEmissao"]].rename(
    columns={
        "CPF_CNPJ_Rem": "node_src",
        "CPF_CNPJ_Des": "node_dest",
        "Produto": "id_product",
        "Volume": "vol",
        "DtEmissao": "date"
    }
)
edges_jan = edges_jan[edges_jan['node_src'] != edges_jan['node_dest']]
edges_jan["date"] = pd.to_datetime(edges_jan["date"], yearfirst=True)
edges_jan.sort_values(['date'], ascending=True, inplace=True)
edges_jan.to_csv("data/edges_jan.csv", index=False)


