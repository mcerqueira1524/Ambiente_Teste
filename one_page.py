import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
import yaml
from yaml.loader import SafeLoader
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import plotly.graph_objects as go
from io import BytesIO
import io
from pyxlsb import open_workbook as open_xlsb
import numpy as np
from st_pages import show_pages_from_config

st.set_page_config(page_title = "Dash 360 IOL", layout="wide", initial_sidebar_state="collapsed")

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Usuário desconhecido ou senha incorreta.")
        return False
    else:
        # Password correct.
        return True
        
if check_password():

    @st.cache_data_clear()

    @st.cache_data
    def importar_pu(): #PU
        df_pu = pd.read_excel(r"Provas Únicas_Tratado.xlsx")
        return df_pu
    
    #importando o Dash 360 de 2023
    @st.cache_data
    def importar_dash360():
        df_dash360 = pd.read_excel(r"Dash 360 Final_Tratado.xlsx")
        return df_dash360

    @st.cache_data
    def importar_baseshist():
        df_baseshist = pd.read_excel(r"Base compilada 2019 a 2022.xlsx")
        return df_baseshist

    df_dash360 = importar_dash360()
    df_baseshist= importar_baseshist()
    df_pu = importar_pu()

    #selecionar no dash 2023 as colunas que tem no 2019-2022
    df_dash360_cols = df_dash360[['ID',
                                'Nome',
                                'Serie',
                                'Status',
                                'Praça Aluno',
                                'Tipo',
                                'Praça']]

    df_dash360_cols['Base Ano'] = 2023 #adicionando a coluna ano=2023
    df_dash360_cols = df_dash360_cols[df_dash360_cols['Nome'].notnull()] #filtrando apenas os que tem nome na base tratada 2023

    #juntar as bases 2019-2022 & 2023
    frames = [df_baseshist,df_dash360_cols]
    df_selection = pd.concat(frames, ignore_index=True, sort=False)

    df_selection['cont'] = 1

    ##Padronização de gráficos
    template_dash = "plotly_white"
    bg_color_dash = "rgba(0,0,0,0)"
    #cores nessa ordem: Rosa choque; Amarelo; Azul escuro; verdinho; azul normal; salmão; verdinho escuro; Azul clarinho; laranja claro;
    colors = ['#EE2D67','#EBEA70','#002561','#8EC6B2','#008ED4','#F2665E', '#55AA8C','#C4ECFF','#FCBD7D']

    ### Layout ###
    st.title("Informações Gerais",anchor=None)
    st.markdown("<h5 style='text-align: center;'>Quantidade de alunos</h5>", unsafe_allow_html=True)

    #primeira linha - informações de qtd de alunos
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        qtd_ativos_2019 = df_selection[(df_selection['Base Ano'] == 2019)]['cont'].sum()
        qtd_desligados_2019 = df_selection[((df_selection['Status'] == 'AFASTADO') | (df_selection['Status'] == 'DESLIGADO'))& (df_selection['Base Ano'] == 2019)]['cont'].sum()
        st.metric("Alunos iniciais - 2019:",qtd_ativos_2019, delta= "-" + str(qtd_desligados_2019) + " desligados/afastados", delta_color="normal", help=None)

    with col2:
        qtd_ativos_2020 = df_selection[(df_selection['Base Ano'] == 2020)]['cont'].sum()
        qtd_desligados_2020 = df_selection[((df_selection['Status'] == 'AFASTADO') | (df_selection['Status'] == 'DESLIGADO'))& (df_selection['Base Ano'] == 2020)]['cont'].sum()
        st.metric("Alunos iniciais - 2020:",qtd_ativos_2020, delta="-" + str(qtd_desligados_2020) + " desligados/afastados", delta_color="normal", help=None)

    with col3:
        qtd_ativos_2021 = df_selection[(df_selection['Base Ano'] == 2021)]['cont'].sum()
        qtd_desligados_2021 = df_selection[((df_selection['Status'] == 'AFASTADO') | (df_selection['Status'] == 'DESLIGADO'))& (df_selection['Base Ano'] == 2021)]['cont'].sum()
        st.metric("Alunos iniciais - 2021:",qtd_ativos_2021, delta="-"+ str(qtd_desligados_2021) + " desligados/afastados", delta_color="normal", help=None)

    with col4:
        qtd_ativos_2022 = df_selection[(df_selection['Base Ano'] == 2022)]['cont'].sum()
        qtd_desligados_2022 = df_selection[((df_selection['Status'] == 'AFASTADO') | (df_selection['Status'] == 'DESLIGADO'))& (df_selection['Base Ano'] == 2022)]['cont'].sum()
        st.metric("Alunos iniciais - 2022:",qtd_ativos_2022, delta="-"+ str(qtd_desligados_2022) + " desligados/afastados", delta_color="normal", help=None)

    with col5:
        qtd_ativos_2023 = df_selection[(df_selection['Base Ano'] == 2023)]['cont'].sum()
        qtd_desligados_2023 = df_selection[((df_selection['Status'] == 'AFASTADO') | (df_selection['Status'] == 'DESLIGADO'))& (df_selection['Base Ano'] == 2023)]['cont'].sum()
        st.metric("Alunos iniciais - 2023:",qtd_ativos_2023, delta="-"+ str(qtd_desligados_2023) + " desligados/afastados", delta_color="normal", help=None)

    st.markdown("##")
    #expander 1 = grafico com qtd de alunos por ano/série
    expander1=st.expander('Quantidade de alunos - detalhamento:')
    with expander1:
        st.write('Quantidade de alunos por série:')
        ##Quantidade de alunos por série

        quant_serie = df_selection.groupby(by=['Base Ano','Serie']).size().reset_index()
        quant_serie['quantidade'] = quant_serie.loc[:,0]

        fig_quant_serie = px.bar(
            quant_serie,
            x="Base Ano",
            y="quantidade",
            text = "quantidade",
            color = "Serie",
            color_discrete_sequence = colors,
            template = template_dash,
            barmode='stack'
        )

        fig_quant_serie.update_traces(texttemplate='%{y}',
                                    textposition='inside',
                                    #textfont_size=11,
                                    textangle=0,
                                    insidetextanchor = 'middle'
                                    )

        fig_quant_serie.update_xaxes(tickfont=dict(size=11))

        fig_quant_serie.update_yaxes(visible=False)

        fig_quant_serie.update_layout(legend=dict(
            yanchor="top",
            y=1.11,
            xanchor="right",
            x=0.05),
            font=dict(size=12)
            )

        #plotando o gráfico na tela
        st.plotly_chart(fig_quant_serie,use_container_width=True)

        ### gráfico por praça
        st.markdown("##")
        st.write('Quantidade de alunos por praça:')

        quant_praca = df_selection.groupby(by=['Base Ano','Praça']).size().reset_index()
        quant_praca['quantidade'] = quant_praca.loc[:,0]

        fig_quant_praca = px.bar(
            quant_praca,
            x="Base Ano",
            y="quantidade",
            text = "quantidade",
            color = "Praça",
            color_discrete_sequence = colors,
            template = template_dash,
            barmode='stack'
        )

        fig_quant_praca.update_traces(texttemplate='%{y}',
                                    textposition='inside',
                                    #textfont_size=11,
                                    textangle=0,
                                    insidetextanchor = 'middle'
                                    )

        fig_quant_praca.update_xaxes(tickfont=dict(size=11))

        fig_quant_praca.update_yaxes(visible=False)

        fig_quant_praca.update_layout(legend=dict(
            yanchor="top",
            y=1.11,
            xanchor="right",
            x=0.05),
            font=dict(size=12)
            )

        #plotando o gráfico na tela
        st.plotly_chart(fig_quant_praca,use_container_width=True)

    st.markdown("##")
    st.markdown("---")

    #segunda linha = informação de notas PU
    st.markdown("<h5 style='text-align: center;'>Prova Única</h5>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        media_2019 = round(df_pu[(df_pu['YYYY'] == 2019) & (df_pu['Área'] == 'Média Geral')]['ENEM_Projetado'].mean())
        st.metric("PU 2019:", media_2019, delta_color="normal", help = None)

    with col2:
        media_2020 = round(df_pu[(df_pu['YYYY'] == 2020) & (df_pu['Área'] == 'Média Geral')]['ENEM_Projetado'].mean())
        st.metric("PU 2020:", media_2020, delta_color="normal", help = None)

    with col3:
        media_2021 = round(df_pu[(df_pu['YYYY'] == 2021) & (df_pu['Área'] == 'Média Geral')]['ENEM_Projetado'].mean())
        st.metric("PU 2021:", media_2021, delta_color="normal", help = None)

    with col4:
        media_2022 = round(df_pu[(df_pu['YYYY'] == 2022) & (df_pu['Status 2022'] == 'ATIVO') & (df_pu['Área'] == 'Média Geral')]['ENEM_Projetado'].mean())
        st.metric("PU 2022:", media_2022, delta_color="normal", help = None)

    with col5: ## precisa filtrar os ativos
        media_2023 = round(df_pu[(df_pu['YYYY'] == 2023) & (df_pu['Área'] == 'Média Geral')]['ENEM_Projetado'].mean())
        st.metric("PU 2023:", media_2023, delta_color="normal", help = None)

    st.markdown("##")
    #expander 2 = grafico boxplot com média de pu projetada por ano/série
    expander2=st.expander('Boxplot de PU Projetada - Detalhamento:')
    with expander2:
        st.write("PU Projetada por série")

        col1, espaco1 = st.columns([1,4])
        with col1:
            #escolha a sua PU
            prova_ano_select = st.selectbox('Qual das três provas únicas?',('PU 1', 'PU 2', 'PU 3'))

        #filtrando o df da PU
        pu_boxplot = df_pu[['YYYY','SÉRIE','Área',
                            'Prova Ano','ENEM_Projetado']][(df_pu['Área'] == 'Média Geral') 
                                                           & (df_pu['Prova Ano'] == prova_ano_select)
                                                           & (df_pu['YYYY'] > 2019)]

        fig_pu_boxplot = px.box(
            pu_boxplot,
            x='YYYY',
            y='ENEM_Projetado',
            color='SÉRIE',
            color_discrete_map = {'EF_8':'#002561','EF_9':'#EBEA70','EM_1':'#EE2D67','EM_2':'#8EC6B2','EM_3':'#F2665E'},
            category_orders={'YYYY':[2019,2020,2021,2022,2023]},
            template = template_dash
        )

        fig_pu_boxplot.update_layout(
            xaxis_title="Ano",
            yaxis_title="ENEM Projetado",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> DISTRIBUIÇÃO ENEM PROJETADA POR SÉRIE </b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_pu_boxplot.update_yaxes(range=[100, 900])

        fig_pu_boxplot.update_traces(boxmean = True)

        st.plotly_chart(fig_pu_boxplot,use_container_width=True)

    st.markdown("---")
    st.markdown("<h5 style='text-align: center;'>ENEM</h5>", unsafe_allow_html=True)
    col2, col3, col4, col5 = st.columns(4)
    with col2:
        enem_2020 = round(df_selection[(df_selection['ENEM  - Informou ENEM?'] == 'SIM') & (df_selection['Base Ano'] == 2020) & (df_selection['Status'] == 'ATIVO')]['ENEM - Média simples'].mean())
        st.metric("ENEM 2020:", enem_2020, delta_color="normal", help=None)

    with col3:
        enem_2021 = round(df_selection[(df_selection['ENEM  - Informou ENEM?'] == 'SIM') & (df_selection['Base Ano'] == 2021) & (df_selection['Status'] == 'ATIVO')]['ENEM - Média simples'].mean())
        st.metric("ENEM 2021:", enem_2021, delta_color="normal", help=None)

    with col4:
        enem_2022 = round(df_selection[(df_selection['ENEM  - Informou ENEM?'] == 'SIM') & (df_selection['Base Ano'] == 2022) & (df_selection['Status'] == 'ATIVO')]['ENEM - Média simples'].mean())
        st.metric("ENEM 2022:", enem_2022, delta_color="normal", help=None)

    with col5:
        st.metric("ENEM 2023:",'-' , delta_color="normal", help=None)


    expander5=st.expander('Boxplot de desempenho ENEM - Detalhamento:')
    with expander5:
        st.write('Boxplot de desempenho ENEM por praça:')
        #filtrando df ENEM
        enem_boxplot = df_selection[(df_selection['ENEM  - Informou ENEM?'] == 'SIM')
                                    & (df_selection['Status'] == 'ATIVO')
                                    & (df_selection['Base Ano'] > 2019)][['Base Ano','ENEM - Média simples','Tipo','Praça']]
        enem_boxplot = enem_boxplot.sort_values(by=['Base Ano']) #ordenar os anos na ordem certa
        enem_boxplot['Base Ano'] = enem_boxplot['Base Ano'].astype(str) # plotly estava entendendo o ano como número

        fig_enem_boxplot = px.box(
            enem_boxplot,
            x='Base Ano',
            y='ENEM - Média simples',
            color='Praça',
            template = template_dash,
            color_discrete_sequence = colors
        )

        fig_enem_boxplot.update_layout(
            xaxis_title="Ano",
            yaxis_title="ENEM Média Simples",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> DISTRIBUIÇÃO ENEM PROJETADA POR PRAÇA </b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_enem_boxplot.update_yaxes(range=[100, 900])

        fig_enem_boxplot.update_xaxes(type='category')

        fig_enem_boxplot.update_traces(boxmean = True)

        st.plotly_chart(fig_enem_boxplot,use_container_width=True)

        ### gráfico por praça
        st.markdown("##")
        st.write('Boxplot de desempenho ENEM por tipo:')

        fig_enem_tipo_boxplot = px.box(
            enem_boxplot,
            x='Base Ano',
            y='ENEM - Média simples',
            color='Tipo',
            color_discrete_map = {'EAD':'#8EC6B2','MO':'#008ED4','EPP':'#002561'},
            template = template_dash
        )

        fig_enem_tipo_boxplot.update_layout(
            xaxis_title="Ano",
            yaxis_title="ENEM Média Simples",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> DISTRIBUIÇÃO ENEM PROJETADA POR TIPO </b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_enem_tipo_boxplot.update_yaxes(range=[100, 900])

        fig_enem_tipo_boxplot.update_traces(boxmean = True)

        st.plotly_chart(fig_enem_tipo_boxplot,use_container_width=True)

    hide_st_style="""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-9s5bis {visibility: visible;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
