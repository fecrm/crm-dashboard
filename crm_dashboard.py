import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -------- Simulação de dados --------
data = {
    'CNPJ': [f'Cliente_{i}' for i in range(1, 301)],
    'Canal': ['Email'] * 60 + ['Push'] * 80 + ['WhatsApp'] * 70 + ['SMS'] * 50 + ['InApp'] * 40,
    'Campanha': ['Campanha A'] * 50 + ['Campanha B'] * 50 + ['Campanha C'] * 100 + ['Campanha D'] * 50 + ['Campanha E'] * 50,
    'Indicador_de_Negocio': ['Abertura de Conta'] * 100 + ['Money In'] * 100 + ['DDA'] * 100,
    'Data_Envio': [datetime(2025, 7, 1) + timedelta(days=i % 7) for i in range(300)],
    'Engajado': [True] * 210 + [False] * 90,
    'Data_Engajamento': [datetime(2025, 7, 2) + timedelta(days=i % 5) if i < 210 else None for i in range(300)],
    'Convertido': [True] * 120 + [False] * 180,
    'Data_Acao_Negocio': [datetime(2025, 7, 3) + timedelta(days=i % 7) if i < 120 else None for i in range(300)]
}
df = pd.DataFrame(data)
df['Diferença_Dias'] = (pd.to_datetime(df['Data_Acao_Negocio']) - pd.to_datetime(df['Data_Engajamento'])).dt.days

# -------- Filtros (Seção 1) --------
st.sidebar.header('Filtros do Dashboard')
canal_sel = st.sidebar.multiselect('Canal', df['Canal'].unique(), df['Canal'].unique())
campanha_sel = st.sidebar.multiselect('Nome da Campanha', df['Campanha'].unique(), df['Campanha'].unique())
indicador_sel = st.sidebar.multiselect('Indicador de Negócio', df['Indicador_de_Negocio'].unique(), df['Indicador_de_Negocio'].unique())
data_min, data_max = st.sidebar.date_input('Intervalo de Envio', [df['Data_Envio'].min(), df['Data_Envio'].max()])
status_conv_sel = st.sidebar.selectbox('Status de Conversão', ['Todos', 'Sim', 'Não'])

# -------- Aplicação dos filtros --------
df_filt = df[
    (df['Canal'].isin(canal_sel)) &
    (df['Campanha'].isin(campanha_sel)) &
    (df['Indicador_de_Negocio'].isin(indicador_sel)) &
    (df['Data_Envio'] >= pd.to_datetime(data_min)) &
    (df['Data_Envio'] <= pd.to_datetime(data_max))
]
if status_conv_sel == 'Sim':
    df_filt = df_filt[df_filt['Convertido'] == True]
elif status_conv_sel == 'Não':
    df_filt = df_filt[df_filt['Convertido'] == False]

# -------- Seção 2: Visões Estratégicas --------
st.title('📊 Dashboard CRM → Negócio')

# Funil de Conversão
total = len(df_filt)
engajados = df_filt['Engajado'].sum()
convertidos = df_filt['Convertido'].sum()
fig_funnel = go.Figure(go.Funnel(
    y=['Impactados', 'Engajados', 'Converteram'],
    x=[total, engajados, convertidos],
    marker={"color": ["#1f77b4", "#2ca02c", "#d62728"]}
))
st.subheader('1. Funil CRM → Ação de Negócio')
st.plotly_chart(fig_funnel, use_container_width=True)

# Conversão por canal
st.subheader('2. Taxa de Conversão por Canal')
canal_conv = df_filt.groupby('Canal')['Convertido'].mean().reset_index()
canal_conv['Taxa de Conversão (%)'] = canal_conv['Convertido'] * 100
fig_bar = px.bar(canal_conv, x='Canal', y='Taxa de Conversão (%)', color='Canal')
st.plotly_chart(fig_bar, use_container_width=True)

# Ranking de campanhas
st.subheader('3. Ranking de Campanhas por Conversão')
camp_ranking = df_filt.groupby(['Campanha', 'Canal']).agg(
    engajados=('Engajado', 'sum'),
    convertidos=('Convertido', 'sum')
).reset_index()
camp_ranking['Taxa de Conversão (%)'] = 100 * camp_ranking['convertidos'] / camp_ranking['engajados'].replace(0, 1)
fig_rank = px.bar(camp_ranking.sort_values('Taxa de Conversão (%)', ascending=False),
                  x='Campanha', y='Taxa de Conversão (%)', color='Canal')
st.plotly_chart(fig_rank, use_container_width=True)

# Lag de conversão
st.subheader('4. Tempo até Conversão (Lag)')
lag_df = df_filt[df_filt['Convertido'] == True]
fig_lag = px.histogram(lag_df, x='Diferença_Dias', nbins=10)
st.plotly_chart(fig_lag, use_container_width=True)

# Curva de conversão acumulada
st.subheader('5. Curva de Conversão Acumulada')
df_curve = lag_df.copy()
df_curve['dias_após_envio'] = (df_curve['Data_Acao_Negocio'] - df_curve['Data_Envio']).dt.days
curve = df_curve.groupby('dias_após_envio')['CNPJ'].nunique().cumsum().reset_index()
fig_curve = px.line(curve, x='dias_após_envio', y='CNPJ', labels={'CNPJ': 'Conversões Acumuladas'})
st.plotly_chart(fig_curve, use_container_width=True)

# Heatmap Canal x Indicador
st.subheader('6. Heatmap Canal x Ação de Negócio')
heat = df_filt.groupby(['Canal', 'Indicador_de_Negocio'])['Convertido'].mean().reset_index()
heat['Taxa de Conversão (%)'] = heat['Convertido'] * 100
fig_heat = px.density_heatmap(heat, x='Indicador_de_Negocio', y='Canal', z='Taxa de Conversão (%)',
                              color_continuous_scale='Blues')
st.plotly_chart(fig_heat, use_container_width=True)

# Detalhamento por cliente
st.subheader('7. Distribuição Detalhada por Cliente')
st.dataframe(df_filt[['CNPJ', 'Canal', 'Campanha', 'Data_Envio', 'Engajado', 'Data_Engajamento',
                      'Convertido', 'Data_Acao_Negocio', 'Diferença_Dias']].sort_values(by='Data_Envio'))

st.caption('🔎 Todas as análises consideram CNPJs únicos, engajamento por canal e conversão após engajamento.')
