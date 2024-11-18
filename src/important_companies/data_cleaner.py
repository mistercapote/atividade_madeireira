
import pandas as pd

def convert_id_to_str(df: pd.DataFrame )-> pd.DataFrame:
    """Converte  as colunas de CPF_CNPJ_Rem e CPF_CNPJ_Des
    para str

    Args:
        df (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    df['CPF_CNPJ_Rem'] = df['CPF_CNPJ_Rem'].astype(str)
    df['CPF_CNPJ_Des'] = df['CPF_CNPJ_Des'].astype(str)
    
    return df