import pandas as pd

df1 = pd.read_csv("data/df_01.csv", low_memory=False)
df2 = pd.read_csv("data/df_02.csv", low_memory=False)
df3 = pd.read_csv("data/df_03.csv", low_memory=False)
df4 = pd.read_csv("data/df_04.csv", low_memory=False)
df5 = pd.read_csv("data/df_05.csv", low_memory=False)
df6 = pd.read_csv("data/df_06.csv", low_memory=False)
df = pd.concat([df1, df2, df3, df4, df5, df6], ignore_index=True)

origem = df[["CPF_CNPJ_Rem", "LatOrigem", "LongOrigem", "TpRem"]].rename(
    columns={
    'CPF_CNPJ_Rem': 'id_emp', 
    'LatOrigem': 'latitude', 
    'LongOrigem': 'longitude', 
    'TpRem': 'type'
})
destino = df[["CPF_CNPJ_Des", "LatDestino", "LongDestino", "TpDes"]].rename(
    columns={
    'CPF_CNPJ_Des': 'id_emp', 
    'LatDestino': 'latitude', 
    'LongDestino': 'longitude', 
    'TpDes': 'type'
})
nodes = pd.concat([origem, destino], ignore_index=True)
nodes.drop_duplicates("id_emp", inplace=True)
nodes.to_csv("nodes.csv", index=False)

edges = df[["CPF_CNPJ_Rem", "CPF_CNPJ_Des", "Produto", "Volume", "DtEmissao"]].rename(
    columns={
        "CPF_CNPJ_Rem": "node_src",
        "CPF_CNPJ_Des": "node_dest",
        "Produto": "id_product",
        "Volume": "vol",
        "DtEmissao": "date"
    }
)
edges = edges[edges['node_src'] != edges['node_dest']]
edges["date"] = pd.to_datetime(edges["date"], yearfirst=True)
edges.sort_values(['date'], ascending=True, inplace=True)
edges.to_csv("edges.csv", index=False)