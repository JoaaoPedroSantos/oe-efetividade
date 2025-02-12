import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def create_projection_coverage_plot(df_simula, df_fato, df_grafico_cobertura, lista_av, data_lib, transit, lead, d_final):
    # Garantir que as datas de vistoria estejam na segunda-feira
    lista_av['data_vistoria_afa'] = pd.to_datetime(lista_av['data_vistoria_afa'])
    lista_av['data_vistoria_afa'] -= pd.to_timedelta(lista_av['data_vistoria_afa'].dt.weekday, unit='D')

    # Definir as cores para o gráfico de barras
    cores = {'STK': 'green', 'INVOI': 'blue', 'PO': 'yellow', 'OP': 'purple', 'DEMAND': 'red'}

    # Criando o gráfico de barras
    grafico_cobertura = px.bar(
        df_grafico_cobertura,
        x="data",
        y=[1] * len(df_grafico_cobertura),  # Mantém altura fixa para as barras
        color="status",
        color_discrete_map=cores,
    )

    # Criando a figura com subplots e eixo X comum
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        subplot_titles=("Projeção Fato vs Simulação", "Gráfico de Cobertura"),
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1
    )

    # Adicionando a projeção simulação (df_simula)
    fig.add_trace(go.Scatter(
        x=df_simula['data'],
        y=df_simula['projecao'],
        mode='lines+markers',
        name='Projeção Simulação',
        marker=dict(color='lightgreen')
    ), row=1, col=1)

    # Adicionando a projeção fato (df_fato)
    fig.add_trace(go.Scatter(
        x=df_fato['data'],
        y=df_fato['projecao'],
        mode='lines+markers',
        name='Projeção Fato',
        marker=dict(color='blue')
    ), row=1, col=1)

    # Adicionando os pontos de vistoria da lista_av
    lista_av = lista_av.merge(df_simula[['data', 'projecao']], left_on='data_vistoria_afa', right_on='data', how='left')
    fig.add_trace(go.Scatter(
        x=lista_av['data_vistoria_afa'],
        y=lista_av['projecao'],  # Posição de acordo com df_simula
        mode='markers',
        name='DANE',
        marker=dict(color='darkturquoise', size=10, symbol='circle'),
        text=lista_av['numero_serie_aeronave'],
        hoverinfo='text'
    ), row=1, col=1)

    # Lista de eventos com datas, cores e nomes
    eventos = [
        (data_lib, "blue", "DtLib"),
        (transit, "orange", "TransitTime"),
        (lead, "red", "LeadTime"),
        (d_final, "green", "DFinal")
    ]

    # Definir limites do eixo Y
    y_min = min(df_simula['projecao'].min(), df_fato['projecao'].min())
    y_max = max(df_simula['projecao'].max(), df_fato['projecao'].max())

    # Função para adicionar linhas verticais e legendas ao lado
    def add_vertical_line(fig, x_value, color, text, y_ref):
        fig.add_shape(
            type="line",
            x0=x_value,
            x1=x_value,
            y0=y_min,
            y1=y_max,
            line=dict(color=color, width=2, dash="dash")
        )

        fig.add_trace(go.Scatter(
            x=[x_value],
            y=[y_ref],  # Posição da legenda ao lado
            mode="text",
            text=[text],
            textposition="middle right",
            showlegend=False,
            textfont=dict(size=12, color=color)
        ), row=1, col=1)

    # Gerando posições dinâmicas para evitar sobreposição
    num_eventos = len(eventos)
    y_ref_positions = [y_max * (0.95 - 0.1 * i) for i in range(num_eventos)]

    # Adicionando as linhas verticais e legendas ao lado
    for (x_value, color, text), y_ref in zip(eventos, y_ref_positions):
        add_vertical_line(fig, x_value, color, text, y_ref)

    # Adicionando as barras de cobertura (grafico_cobertura)
    for trace in grafico_cobertura.data:
        fig.add_trace(trace, row=2, col=1)

    fig.update_layout(
        title=f'Projeção Fato vs Simulação e Cobertura',
        yaxis_title='Projeção',
        yaxis=dict(range=[y_min - 0.1 * (y_max - y_min), y_max + 0.1 * (y_max - y_min)]),  # Limites do eixo Y
        yaxis2=dict(range=[0, 1]),  # Limites do eixo Y do gráfico de barras (altura fixa)
        xaxis=dict(range=[df_simula['data'].min() -  pd.Timedelta(days=3), df_simula['data'].max() + pd.Timedelta(days=3)]),  # Definindo limites fixos para o eixo X
        template='plotly_white',
        showlegend=True
    )

    return fig