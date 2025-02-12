import pandas as pd

def projecao(ne, data_ini, full_df):
    full_df = full_df.copy()

    # Calcula a projeção cumulativa
    variacao = full_df['quantidade_convertida'] - full_df['quantidade_demanda']
    nivel = ne + variacao.cumsum()

    # Cria as colunas de projeção e passo
    full_df = full_df.assign(projecao=nivel, passo=range(1, len(full_df) + 1))

    # Criando o primeiro registro inicial
    df_ini = pd.DataFrame([{
        "key_cluster_material": full_df['key_cluster_material'].iloc[0],
        "quantidade_demanda": 0,
        "quantidade_convertida": 0,
        "status_documento": 'INI',
        "data": data_ini,
        "projecao": ne,
        "passo": 0
    }])

    # Concatena o registro inicial ao DataFrame original
    df = pd.concat([df_ini, full_df], ignore_index=True)

    # Garante que a coluna 'data' está no formato datetime
    df['data'] = pd.to_datetime(df['data'], errors='coerce')

    return df

def inserir_demanda(acao,lista_d, full_df):
    lista_d['data_vistoria_afa'] = pd.to_datetime(lista_d['data_vistoria_afa'])
    lista_d['data_vistoria_afa'] = lista_d['data_vistoria_afa'] - pd.to_timedelta(lista_d['data_vistoria_afa'].dt.weekday, unit='D')

    # Renomeando colunas
    lista_d.columns = ['data', 'quantidade_demanda']
    lista_d['quantidade_demanda'] = lista_d['quantidade_demanda'] * acao

    # Concatenando os DataFrames
    df_simu = pd.concat([full_df, lista_d], ignore_index=True)

    # Agrupando por data e somando as colunas numéricas
    df_grouped = df_simu.groupby("data", as_index=False).sum()

    # Ordenando os dados por data
    df_grouped = df_grouped.sort_values(by="data")

    return df_grouped