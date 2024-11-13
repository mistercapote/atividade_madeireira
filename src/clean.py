import pandas as pd

df = pd.read_csv("data/df_01.csv", low_memory=False)

origem = df[["CPF_CNPJ_Rem", "LatOrigem", "LongOrigem", "TpRem"]].rename(
    columns={
    'CPF_CNPJ_Rem': 'CPF_CNPJ', 
    'LatOrigem': 'Latitude', 
    'LongOrigem': 'Longitude', 
    'TpRem': 'Tipo'
})
destino = df[["CPF_CNPJ_Des", "LatDestino", "LongDestino", "TpDes"]].rename(
    columns={
    'CPF_CNPJ_Des': 'CPF_CNPJ', 
    'LatDestino': 'Latitude', 
    'LongDestino': 'Longitude', 
    'TpDes': 'Tipo'
})
nodes = pd.concat([origem, destino], ignore_index=True)
nodes.drop_duplicates("CPF_CNPJ", inplace=True)
nodes["Coordenada"] = nodes.apply(lambda row: (row['Latitude'], row['Longitude']), axis=1)
nodes.drop(["Latitude", "Longitude"], axis=1, inplace=True)
nodes.to_csv("nodes.csv", index=False)

edges = df[["CPF_CNPJ_Rem", "CPF_CNPJ_Des", "Produto", "Volume", "DtEmissao"]]
edges = edges[edges['CPF_CNPJ_Rem'] != edges['CPF_CNPJ_Des']]
# edges["DtEmissao"] = pd.to_datetime(edges["DtEmissao"], yearfirst=True)
edges.sort_values(['DtEmissao'], ascending=True, inplace=True)
edges.to_csv("edges.csv", index=False)