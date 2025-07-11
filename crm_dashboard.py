import streamlit as st
import pandas as pd
import plotly.express as px

# --------- Simula dados ---------
data = {
    'CNPJ': [f'Cliente_{i}' for i in range(1, 301)],
    'Canal': ['Email'] * 100 + ['Push'] * 100 + ['WhatsApp'] * 100,
    'Campanha': ['Campanha A'] * 50 + ['Campanha B'] * 50 + ['Campanha C'] * 100 + ['Campanha D'] * 100,
    'Indicador_de_Negocio': ['Abertura de Conta'] * 150 + ['Money In'] * 150,
    'Engajado': [True] * 200 + [False] * 100,
    'Convertido': [True] * 90 + [False] * 210,
    'Dias_ate_conversao': [1, 2, 3, 4, 5, 6, 7, 3, 2, 1] * 9 + [None] * 210
}
df = pd.DataFrame(data)

# --------- Sidebar - Filtros ---------
st.sidebar.title('Filtros')
canal_sel = st.sidebar.multiselect('Canal', df['Canal'].unique(), default=df['Canal'].unique())
campanha_sel = st.sidebar.multiselect('Campanha', df['Campanha'].unique(), default=df['Campanha'].unique())
indicador_sel = st.sidebar.multiselect('Indicador de Negócio', df['Indicador_de_Negocio'].unique(), default=df['Indicador_de_Negocio'].unique())
status_conv_sel = st.sidebar.selectbox('Status de Conversão', ['Todos', 'Sim', 'Não'])

# --------- Filtro base ---------
df_filtrado = df[df['Canal'].isin(canal_sel) & df['Campanha'].isin(campanha_sel) & df['Indicador_de_Negocio'].isin(indicador_sel)]
if status_conv_sel == 'Sim':
    df_filtrado = df_filtrado[df_filtrado['Convertido'] == True]
elif status_conv_sel == 'Não':
    df_filtrado = df_filtrado[df_filtrado['Convertido'] == False]

# --------- Funil ---------
st.header('Funil de Engajamento → Conversão')
total = len(df_filtrado)
engajados = df_filtrado['Engajado'].sum()
convertidos = df_filtrado['Convertido'].sum()

st.metric('Impactados', total)
st.metric('Engajados', engajados)
st.metric('Converteram', convertidos)

# --------- Taxa por canal ---------
st.subheader('Taxa de Conversão por Canal')
canal_conv = df_filtrado.groupby('Canal').agg({'Convertido': 'mean'}).reset_index()
canal_conv['Convertido'] = canal_conv['Convertido'] * 100
fig1 = px.bar(canal_conv, x='Canal', y='Convertido', labels={'Convertido': 'Taxa de Conversão (%)'})
st.plotly_chart(fig1, use_container_width=True)

# --------- Ranking campanhas ---------
st.subheader('Ranking de Campanhas por Conversão')
camp_conv = df_filtrado.groupby('Campanha').agg({'Convertido': 'mean'}).reset_index()
camp_conv['Convertido'] = camp_conv['Convertido'] * 100
fig2 = px.bar(camp_conv.sort_values('Convertido', ascending=False), x='Campanha', y='Convertido', labels={'Convertido': 'Taxa de Conversão (%)'})
st.plotly_chart(fig2, use_container_width=True)

# --------- Lag Time ---------
st.subheader('Tempo até Conversão (Lag em dias)')
lag_data = df_filtrado[df_filtrado['Convertido'] == True]
fig3 = px.histogram(lag_data, x='Dias_ate_conversao', nbins=10, labels={'Dias_ate_conversao': 'Dias até Conversão'})
st.plotly_chart(fig3, use_container_width=True)

# --------- Heatmap Canal x Indicador ---------
st.subheader('Mapa de Calor: Canal x Indicador de Negócio')
heat = df_filtrado.groupby(['Canal', 'Indicador_de_Negocio']).agg({'Convertido': 'mean'}).reset_index()
heat['Convertido'] = heat['Convertido'] * 100
fig4 = px.density_heatmap(heat, x='Indicador_de_Negocio', y='Canal', z='Convertido', color_continuous_scale='Blues', labels={'Convertido': 'Taxa de Conversão (%)'})
st.plotly_chart(fig4, use_container_width=True)

st.caption('Dashboard simulado para análises de CRM com base em engajamento e comportamento de negócio.')
