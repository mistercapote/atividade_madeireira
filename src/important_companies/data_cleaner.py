
import pandas as pd

def convert_id_to_str(df: pd.DataFrame )-> pd.DataFrame:
    
    df['CPF_CNPJ_Rem'] = df['CPF_CNPJ_Rem'].astype(str)
    df['CPF_CNPJ_Des'] = df['CPF_CNPJ_Des'].astype(str)
    
    return df