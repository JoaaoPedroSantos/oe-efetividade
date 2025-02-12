import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from manager.projecao import projecao, inserir_demanda
from manager.cobertura import cobertura
from manager.visual import create_projection_coverage_plot

# Configuração do layout padrão (wide mode e tema escuro)
st.set_page_config(layout="wide", page_title="Simulação de Projeção", page_icon="📊")
st.markdown("""
    <style>
        body { color: white; background-color: #0e1117; }
        .stApp { background-color: #0e1117; }
    </style>
""", unsafe_allow_html=True)

# Carregamento dos dados
merged_df = pd.read_csv('data/merged_df.csv')
oe_final = pd.read_csv('data/oe_final.csv')
cod_av = pd.read_csv('data/cod_av.csv')


oe_final.drop(columns = 'data_referencia_semana', inplace = True)
# Processamento inicial
oe_final['Material'] = oe_final['Material'].astype(str)
cod_av['OE'] = np.where(cod_av['codigo_tipo'] == 390, '390011813-00', '190310172-00')
cod_av['data_vistoria_afa'] = pd.to_datetime(cod_av['data_vistoria_afa']) - pd.DateOffset(months=2)

# Interface Streamlit
st.title("📊 Simulação de Projeção e Cobertura")

# Seleção de Material
materiais_disponiveis = oe_final['Material'].unique()
materiais_filtrados = [m for m in materiais_disponiveis if m != '807155']
material = st.selectbox("🛠️ Selecione o Material", materiais_filtrados, index=materiais_filtrados.index('184503'))

# Exibir dados do material selecionado com labels
st.subheader("📌 Informações do Material Selecionado")
material_data = oe_final[oe_final['Material'] == material].iloc[0]

st.dataframe(oe_final[oe_final['Material'] == material].iloc[:, :11])
st.dataframe(oe_final[oe_final['Material'] == material].iloc[:, 11:])

ne = material_data['saldo_estoque']
full_df = merged_df[merged_df.key_cluster_material == f'SAP ONE_{material}'].reset_index(drop=True).copy()
full_df['data'] = pd.to_datetime(full_df['data'])

# Configuração das datas
data_ini = full_df.data.iloc[0] - pd.Timedelta(weeks=1) if not full_df.empty else None

# Ação (Excluir ou Incluir)
acao_map = {"Excluir": -1, "Incluir": 1}
acao_text = st.selectbox("🔄 Escolha a Ação", list(acao_map.keys()))
acao = acao_map[acao_text]

# Seleção de quantidade de itens na lista_av
lista_av = cod_av[cod_av.OE == cod_av.OE.unique()[1]]
lista_av.loc[lista_av.index[2], 'data_vistoria_afa'] = pd.to_datetime('2025-02-28')
num_items = st.slider("✈️ Quantidade DANE", 1, len(lista_av), (0, len(lista_av)))

lista_av = lista_av.iloc[num_items[0]:num_items[1]]

cod = lista_av.numero_serie_aeronave.unique()
lista_d = lista_av[['data_vistoria_afa', 'qtd_demanda']]

# Projeção e simulação
df_fato = projecao(ne, data_ini, full_df)
df_simula = projecao(ne, data_ini, inserir_demanda(acao, lista_d, full_df))

# Cálculo de datas e custos
data_lib = full_df.data.iloc[0] - pd.Timedelta(weeks=1)
transit = df_fato['data'][0] + pd.offsets.BusinessDay(material_data['tempo_entrada_material_dias'])
lead = transit + pd.to_timedelta(material_data['leadtime_dias'], unit='D')
temp_p = data_lib + (lead - lead.normalize())

delta = (lista_av['data_vistoria_afa'].iloc[0] - temp_p).days
custo_sobra = df_simula['projecao'].iloc[-1] * material_data['preco_unitario_usd']
d_final = df_simula['data'].iloc[-1] - pd.Timedelta(days=2)

# Exibição dos resultados
st.subheader("📊 Resultados da Simulação")
st.write(f"💰 **Custo da Sobra:** ${custo_sobra:.2f} USD")
st.write(f"📅 **Delta:** {delta} dias")

# Gráficos
doc = full_df.groupby('status_documento').sum(numeric_only=True)['quantidade_convertida'].reset_index()
cobertura_df = full_df[['data', 'quantidade_demanda']]
df_grafico_cobertura = cobertura(doc, cobertura_df, df_fato)

fig = create_projection_coverage_plot(df_simula, df_fato, df_grafico_cobertura, lista_av, data_lib, transit, lead, d_final)
st.plotly_chart(fig)
