import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(layout="wide")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo .xlsx ou .csv", type=["xlsx", "csv"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file, sep=";", decimal=",")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
    else:
        st.write("O arquivo carregado não contém uma coluna 'Date'. Por favor, carregue um arquivo que contenha uma coluna 'Date'.")

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Adição da coluna 'Month'
    df["Month"] = df["Date"].apply(lambda x: f"{x.year}-{x.month}")
    months = df["Month"].unique()

    # Opção para avaliar o período total ou escolher um mês
    period_option = st.sidebar.radio("Avaliar por:", ["Mês", "Período Total"])

    if period_option == "Mês":
        # Seleção do mês via barra lateral
        selected_month = st.sidebar.selectbox("Mês", months)
        df_filtered = df[df["Month"] == selected_month]
    else:
        # Avaliação para o período total
        df_filtered = df

    # Opção para escolher a coluna para a frequência relativa e acumulada
    selected_column = st.sidebar.selectbox("Selecione a Coluna de Dados (Pareto e ABC):", ["Selecione uma coluna"] + list(df_filtered.columns))

    # Opção para escolher a coluna para o eixo das abscissas
    x_axis_column = st.sidebar.selectbox("Selecione a Coluna dos Itens (Pareto e ABC):", ["Selecione uma coluna"] + list(df_filtered.columns))

    # Layout em colunas
    col1 = st.columns(1)
    col2 = st.columns(1)

    # Verificar se o DataFrame df_filtered contém dados antes de criar o gráfico do Pareto
    if not df_filtered.empty and selected_column != "Selecione uma coluna" and x_axis_column != "Selecione uma coluna":
        # Gráfico de Pareto
        df_pareto = df_filtered.groupby(x_axis_column)[selected_column].sum().sort_values(ascending=False).reset_index()
        df_pareto["pareto_rel"] = (df_pareto[selected_column] / df_pareto[selected_column].sum()) * 100
        df_pareto["pareto_acum"] = df_pareto["pareto_rel"].cumsum()

        # Criando uma segunda escala para a curva de Pareto
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=df_pareto[x_axis_column], y=df_pareto[selected_column], text=df_pareto["pareto_rel"], textposition="auto", name=selected_column))
        fig_pareto.add_trace(go.Scatter(x=df_pareto[x_axis_column], y=df_pareto["pareto_acum"], mode="lines", name="Curva de Pareto", yaxis="y2"))

        # Adicionando rótulos aos eixos
        fig_pareto.update_layout(
            xaxis=dict(title=x_axis_column),
            yaxis=dict(title=selected_column, side="left"),
            yaxis2=dict(title="Curva de Pareto", side="right", overlaying="y", showgrid=False),
            title="Diagrama de Pareto",
        )
        col1[0].plotly_chart(fig_pareto, use_container_width=True)

        # Curva ABC
        df_abc = df_pareto.copy()
        df_abc["Classe_ABC"] = pd.qcut(df_abc["pareto_acum"], q=[0, 0.2, 0.5, 1.0], labels=["A", "B", "C"])

        # Verificar se todas as classes ABC contêm pelo menos um valor
        if all(df_abc["Classe_ABC"].value_counts() > 0):
            # Gráfico de Barras para a Curva ABC
            fig_abc = px.bar(df_abc, x=x_axis_column, y="pareto_acum", color="Classe_ABC", title="Curva ABC")
            # Adicionando rótulos aos eixos
            fig_abc.update_layout(
                xaxis=dict(title=x_axis_column),
                yaxis=dict(title=selected_column, side="left"),
                title="Gráfico da Curva ABC",
            )
            col2[0].plotly_chart(fig_abc, use_container_width=True)
        else:
            st.write("Dados insuficientes para a Curva ABC")
else:
    st.write("Por favor, faça o upload de um arquivo.")

# Permite selecionar um arquivo .xlsx ou .csv, e carrega os dados em um DataFrame;
# Permite avaliar o dashboard em meses e no período total;
# Implementado gráfico do Diagrama de Pareto na Primeira Linha e na Primeira Coluna;
# Implementado gráfico da Curva ABC na Segunda Linha e na Primeira Coluna;
# Permite selecionar os tipos de colunas com dados para o gráfico do Diagrama de Pareto;
# Primeira lista suspensa "Selecione a Coluna de Dados (Pareto e ABC):", refere-se aos dados absolutos, custos totais e etc.;
# Segunda lista suspensa "Selecione a Coluna dos Itens (Pareto e ABC):", refere-se a identificação dos itens, produtos, etc.
