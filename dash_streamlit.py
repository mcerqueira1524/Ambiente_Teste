import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from functools import reduce
from io import BytesIO
from st_pages import Page, Section, add_page_title, show_pages

#teste
favicon = Image.open("favicon.ico")

st.set_page_config(page_title = "Dash 360 IOL 2023", layout="wide", initial_sidebar_state="collapsed")

show_pages(
    [
        Page("leia_me.py", "Leia Me", ":books:"),
        #Page("pages/painel_metas.py", "Painel de Metas", ":dart:"), [[AJUSTAR]]
        Page("dash_streamlit.py", "Dash Macro", ":bar_chart:"),
        Page("dash_micro.py", "Dash Micro", ":female-student:"),
        Page("filtro_base.py", "Filtro e Download Base", ":pushpin:"),
        Page("one_page.py", "Informações Gerais e Históricas", ":1234:"),
    ]
)

#ano atual para facilitar a transição entre anos
ano_hoje = '2023'

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
    #limpar o cache e atualizar as planilhas

    #@st.cache_data.clear()

    #importando dash 360 de 2022 [[AJUSTAR]]
    @st.cache_data
    def importar_dash2022():
        df_dash2022 = pd.read_excel(r"Dash 360 Final_2022.xlsx")
        df_dash2022 = df_dash2022[df_dash2022['Status'] == 'ATIVO']
        return df_dash2022
    
    df_dash2022 = importar_dash2022()

    #importando o Dash 360 de 2023
    @st.cache_data
    def importar_dash360():
        df_dash360 = pd.read_excel(r"Dash 360 Final_Tratado.xlsx")
        return df_dash360
    
    #importando o engajamento histórico por semana
    @st.cache_data
    def importar_historico_2022():
        df_2022 = pd.read_excel(r"Historico_2022_Tratado.xlsx")
        return df_2022

    #importando o engajamento histórico por semana
    @st.cache_data
    def importar_historico_2021():
        df_2021 = pd.read_excel(r"Historico_2021_Tratado.xlsx")
        return df_2021

    @st.cache_data
    def importar_historico_2020():
        df_2020 = pd.read_excel(r"Historico_2020_Tratado.xlsx")
        return df_2020

    df_dash360 = importar_dash360()
    df_2021 = importar_historico_2021()
    df_2020 = importar_historico_2020()
    df_2022 = importar_historico_2022()
    
    meses = ['Abril','Maio','Junho','Julho','Agosto', 'Setembro', 'Outubro', 'Novembro','Dezembro']
    
    #importando o engajamento histórico por mês
    @st.cache_data
    def importar_yoy_2022():
        df_2022_yoy = pd.read_excel(r"Histórico Mensal Engajamento.xlsx", sheet_name = "2022")
        df_2022_yoy = df_2022_yoy[df_2022_yoy['Status'] == "ATIVO"]
        return df_2022_yoy  
    
    @st.cache_data
    def importar_yoy_2021():
        df_2021_yoy = pd.read_excel(r"Histórico Mensal Engajamento.xlsx", sheet_name = "2021")
        df_2021_yoy = df_2021_yoy[df_2021_yoy["Mês"].isin(meses)]
        return df_2021_yoy  

    @st.cache_data
    def importar_yoy_2020():
        df_2020_yoy = pd.read_excel(r"Histórico Mensal Engajamento.xlsx", sheet_name = "2020")
        df_2020_yoy = df_2020_yoy[(df_2020_yoy["Mês"].isin(meses)) & (df_2020_yoy['Status'] == "ATIVO")]
        return df_2020_yoy  
    
    df_2022_yoy = importar_yoy_2022()
    df_2021_yoy = importar_yoy_2021()
    df_2020_yoy = importar_yoy_2020()
    
    #importando tabelas fato auxiliares
    @st.cache_data
    def importar_olimp():
        df_olimp = pd.read_excel(r"Olimpiadas_Tratado.xlsx")
        return df_olimp
    
    @st.cache_data
    def importar_olimp_teste():
        df_olimp_teste = pd.read_excel(r"teste_olimpiadas.xlsx")
        return df_olimp_teste

    @st.cache_data
    def importar_tutoria():
        df_quinzenal = pd.read_excel(r"Acompanhamento Tutoria_Tratado.xlsx")
        return df_quinzenal

    ###### AJUSTAR DAQUI PARA BAIXO ######

    df_olimp = importar_olimp()
    df_olimp_teste = importar_olimp_teste()
    df_quinzenal = importar_tutoria()

    #merge com as tabelas fato
    olimp_merge = df_olimp.drop_duplicates(subset=['ID'])
    olimp_merge = olimp_merge.drop(columns = ['Mês','Data','Série','Nome', 'Olimpíada', 'Status da Inscrição','Status'])

    data_frames = [df_dash360, olimp_merge]
    df_dash360 = reduce(lambda  left,right: pd.merge(left,right,on=['ID'],how='outer'), data_frames)

    #gerando dois dataframes
    #um (principal) apenas com os alunos ativos
    df_dash360_ativo = df_dash360[df_dash360['Status'] == "ATIVO"]

    #um com todos os alunos (a fim de verificar o aumento de desligados etc)
    df_dash360_total = df_dash360

    #gerando os filtros
    #serie = st.sidebar.multiselect(
    #    "Selecione a série:",
    #    options=df_dash360_ativo['Serie'].dropna().unique(),
    #    default=df_dash360_ativo['Serie'].dropna().unique()
    #    )

    #tutor pode desfiltrar
    desfiltrartutor=st.sidebar.button("Desfiltrar Tutor")
    if desfiltrartutor:
        tutor=st.sidebar.multiselect(
            "Selecione o tutor:",
            options=df_dash360_ativo['Tutor'].dropna(),
            default=df_dash360_ativo['Tutor'].dropna().unique()
            )
    else:
        tutor = st.sidebar.multiselect(
            "Selecione o tutor:",
            options=df_dash360_ativo['Tutor'].dropna().unique(),
            default=df_dash360_ativo['Tutor'].dropna().unique()
            )

    tipo = st.sidebar.multiselect(
        "Selecione o tipo:",
        options=df_dash360_ativo['Tipo'].dropna().unique(),
        default=df_dash360_ativo['Tipo'].dropna().unique()
        )

    praca = st.sidebar.multiselect(
        "Selecione a Praça:",
        options=df_dash360_ativo['Praça'].dropna().unique(),
        default=df_dash360_ativo['Praça'].dropna().unique()
        )


    #base com filtros que será usada nos gráficos
    df_selection = df_dash360_ativo.query("Tipo == @tipo & Praça == @praca & Tutor == @tutor")
    df_selection_total = df_dash360_total.query("Tipo == @tipo & Praça == @praca & Tutor == @tutor") #esse df é para o gráfico de status
    df_dash2022 = df_dash2022.query("Tipo == @tipo & Praça == @praca & Tutor == @tutor") #[[AJUSTAR]]
    df_selection_olimp_teste =  df_olimp_teste.query("Tipo == @tipo & Praça == @praca & Tutor == @tutor")

    #Título
    st.title("Dash 360 Ismart Online 2023")
    st.markdown("##")

    #Número total de alunos ativos
    total_alunos = int(df_selection['ID'].count())

    #Formação em 2023 = média das presenças nas formações
    form_1 = (1651/2336)*100
    form_2 = (1098/1553)*100
    form_3 = float('Nan')
    form_4 = float('Nan')

    forms = [form_1,form_2,form_3,form_4] #lista de todas as formações

    presenca_form = np.nanmean(forms) #média das presenças

    #para engajamento em MA e LI, contabilizamos apenas os alunos não dispensados
    df_meta_acad = df_selection[df_selection['É liberado de Matemática ou Linguagens?'] == 'Não dispensado']

    ##se todos os alunos filtrados forem dispensados, precisa de fazer uma conta da fórmula que não conte MA e LI
    if df_meta_acad[df_meta_acad['ALUNO ALTO ENGAJ MA?'] == 'SIM'].empty:
        #Porcentagem de alunos mais de 60% engajamento
        alto_engaj_miss = ((df_selection[df_selection['ALUNO ALTO ENGAJ MISSÃO?'] == 'SIM']['cont'].sum()/df_selection['cont'].sum())*100)
        alto_engaj_red = ((df_selection[df_selection['ALUNO ALTO ENGAJ RED?'] == 'SIM']['cont'].sum()/df_selection['cont'].sum())*100)

        #agregando todos os valores
        engaj = [alto_engaj_red,alto_engaj_miss,presenca_form]
        alto_engaj = round(np.mean(engaj),1)
    else:
        #Porcentagem de alunos mais de 60% engajamento
        alto_engaj_ma = ((df_meta_acad[df_meta_acad['ALUNO ALTO ENGAJ MA?'] == 'SIM']['cont'].sum()/df_meta_acad['cont'].sum())*100)
        alto_engaj_li = ((df_meta_acad[df_meta_acad['ALUNO ALTO ENGAJ LI?'] == 'SIM']['cont'].sum()/df_meta_acad['cont'].sum())*100)
        alto_engaj_miss = ((df_selection[df_selection['ALUNO ALTO ENGAJ MISSÃO?'] == 'SIM']['cont'].sum()/df_selection['cont'].sum())*100)
        alto_engaj_red = ((df_selection[df_selection['ALUNO ALTO ENGAJ RED?'] == 'SIM']['cont'].sum()/df_selection['cont'].sum())*100)

        #agregando todos os valores
        engaj = [alto_engaj_li,alto_engaj_ma,alto_engaj_red,alto_engaj_miss,presenca_form]
        alto_engaj = round(np.mean(engaj),1)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Alunos ativos", value = total_alunos, help = 'Alunos transferidos para o presencial já foram retirados da base')
    with col2:
        st.metric(label="Engajamento Operações", value = alto_engaj, help = 'Média entre alto engajamento em Matemática, Linguagens, Missões, Redação e a Presença em Formações')
    #with col3:
        #st.metric(label="Engajamento AT", value = alto_engaj_at, help = 'Média entre alto engajamento em Matemática, Linguagens e Redação')
    st.markdown("---")

    ##Gráficos
    template_dash = "plotly_white"
    bg_color_dash = "rgba(0,0,0,0)"
    #cores nessa ordem: Rosa choque; Amarelo; Azul escuro; verdinho; azul normal; salmão; verdinho escuro; Azul clarinho; laranja claro;
    colors = ['#EE2D67','#EBEA70','#002561','#8EC6B2','#008ED4','#F2665E', '#55AA8C','#C4ECFF','#FCBD7D']    
    
    ##Status dos alunos
    fig_status = px.pie(
            df_selection_total,
            values = df_selection_total['Status'].value_counts().sort_index().dropna().values, ##INSERIDO O ".VALUES" NO FINAL - 03/05 - GABRIEL LIMA
            names = pd.unique(df_selection_total['Status'].dropna().sort_values()),
            title ='<b> STATUS </b>',
            color = pd.unique(df_selection_total['Status'].dropna().sort_values()),
            color_discrete_map = {'DESLIGADO':'#EE2D67','AFASTADO':'#EBEA70','TRANSFERIDO':'#002561','ATIVO':'#8EC6B2'},
            hole = .4,
            width = 500, height = 500
            )
    fig_status.update_traces(textposition='auto',
                            texttemplate="%{percent:.0%} %{label}",
                            showlegend=False,
                            textfont_size=15
                            )
    fig_status.update_layout(uniformtext_minsize=12,
                            title={
                                'text': "<b> STATUS </b>",
                                'y':0.9,
                                'x':0.5,
                                'xanchor': 'center',
                                'yanchor': 'top'}
                            )

    ##Quantidade de alunos por série
    quant_serie = df_selection.groupby(by=['Serie']).size().reset_index()
    quant_serie['quantidade'] = quant_serie.loc[:,0]

    fig_quant_serie = px.bar(
        quant_serie,
        x="Serie",
        y='quantidade',
        text = 'quantidade',
        color = "Serie",
        category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
        template = template_dash,
        color_discrete_sequence=colors
    )

    fig_quant_serie.update_layout(
        showlegend=False,
        xaxis_title="Série",
        yaxis_title="# Quantidade",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> # ESTUDANTES POR SÉRIE </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    fig_quant_serie.update_yaxes(visible=False, showticklabels=False)

    ##Quantidade de praça por serie

    quant_praca = df_selection.groupby(by=['Praça','Serie']).size().reset_index()
    quant_praca['quantidade'] = quant_praca.loc[:,0]

    fig_quant_praca = px.bar(
        quant_praca,
        x="Praça",
        y="quantidade",
        text = "quantidade",
        color = "Serie",
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
        x=0.20),
        font=dict(size=12)
        )

    #Configurando a soma no topo do gráfico
    quant_praca_sum = quant_praca.groupby('Praça').sum()

    fig_quant_praca.add_trace(go.Scatter(
        x=quant_praca_sum.index,
        y=quant_praca_sum['quantidade'],
        text=quant_praca_sum['quantidade'],
        mode='text',
        textposition='top center',
        textfont=dict(size=14),
        showlegend=False
    ))

    fig_quant_praca.update_layout(
        yaxis_title="# Quantidade",
        xaxis_title="Praça",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> # PRAÇA POR SÉRIE </b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    ##Porcentagem de Tipos por Série

    tipo_serie = df_selection.groupby(by=['Serie','Tipo']).size().reset_index()
    tipo_serie['percent']=df_selection.groupby(by=['Serie','Tipo']).size ().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    tipo_serie['percent']=round(tipo_serie['percent']).astype(int)
    tipo_serie['quantidade'] = tipo_serie.loc[:,0]
    tipo_serie = pd.DataFrame(tipo_serie)

    #Ordenar série e tipo
    order_serie = df_selection[['ordem_serie','Serie']].groupby(by=['ordem_serie','Serie']).mean().reset_index() #LIMITEI O DF_SELECTION EM [['ORDEM_SERIE','SERIE']] PARA NÃO FAZER O MEAN EM OUTRAS COLUNAS - 03/05 - GABRIEL LIMA
    order_serie = order_serie[['ordem_serie','Serie']]
    order_serie = pd.DataFrame(order_serie)

    #mesclando as duas
    tipo_serie = tipo_serie.merge(order_serie, left_on='Serie', right_on='Serie')
    tipo_serie = tipo_serie.sort_values(by=['ordem_serie'])

    fig_tipo_serie = px.bar(
        tipo_serie,
        x="Serie",
        y="percent",
        text = "percent",
        color = "Tipo",
        color_discrete_map = {'EAD':'#8EC6B2','MO':'#008ED4','EPP':'#002561'},
        category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
        template = template_dash,
        hover_name="Tipo",
        custom_data = ['quantidade'],
        orientation='v'
    )

    fig_tipo_serie.update_traces(texttemplate='%{y}%',
                                textposition='inside',
                                textfont_size=11,
                                textangle=0,
                                insidetextanchor = 'middle',
                                hovertemplate='Percentual da Série = %{y}% <br>Quantidade de alunos = %{customdata} <br>')

    fig_tipo_serie.update_yaxes(visible=False)

    fig_tipo_serie.update_layout(
        yaxis_title="% Porcentagem",
        xaxis_title="Série",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> % TIPO POR SÉRIE </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    ## Porcentagem de Clusterização por ano

    #2023
    cluster_hj = pd.DataFrame(df_selection['CLUSTER ENGAJAMENTO'].value_counts(normalize=True)*100).reset_index().round()
    #cluster_hj = cluster_hj.rename(columns={"index": "CLUSTER ENGAJAMENTO", "CLUSTER ENGAJAMENTO": ano_hoje})
    cluster_hj = cluster_hj.rename(columns={"proportion": ano_hoje}) #RENOMEANDO CORRETAMENTE A COLUNA - 03/05 - GABRIEL LIMA
    cluster_hj[ano_hoje] = round(cluster_hj[ano_hoje]).astype(int)

    #2022
    cluster_2022 = pd.DataFrame(df_2022['CLUSTER ENGAJAMENTO'].value_counts(normalize=True)*100).reset_index().round()
    #cluster_2022 = cluster_2022.rename(columns={"index": "CLUSTER ENGAJAMENTO", "CLUSTER ENGAJAMENTO": "2022"})
    cluster_2022 = cluster_2022.rename(columns={"proportion": "2022"}) #RENOMEANDO CORRETAMENTE A COLUNA - 03/05 - GABRIEL LIMA
    cluster_2022["2022"] = round(cluster_2022["2022"]).astype(int)

    #2021
    cluster_2021 = pd.DataFrame(df_2021['CLUSTER ENGAJAMENTO'].value_counts(normalize=True)*100).reset_index().round()
    #cluster_2021 = cluster_2021.rename(columns={"index": "CLUSTER ENGAJAMENTO", "CLUSTER ENGAJAMENTO": "2021"})
    cluster_2021 = cluster_2021.rename(columns={"proportion": "2021"}) #RENOMEANDO CORRETAMENTE A COLUNA - 03/05 - GABRIEL LIMA
    cluster_2021["2021"] = round(cluster_2021["2021"]).astype(int)

    #2020
    cluster_2020 = pd.DataFrame(df_2020['CLUSTER ENGAJAMENTO'].value_counts(normalize=True)*100).reset_index().round()
    #cluster_2020 = cluster_2020.rename(columns={"index": "CLUSTER ENGAJAMENTO", "CLUSTER ENGAJAMENTO": "2020"})
    cluster_2020 = cluster_2020.rename(columns={"proportion": "2020"}) #RENOMEANDO CORRETAMENTE A COLUNA - 03/05 - GABRIEL LIMA
    cluster_2020["2020"] = round(cluster_2020["2020"]).astype(int)
    
    #juntando todas as tabelas
    data_frames = [cluster_hj, cluster_2021, cluster_2020, cluster_2022]
    cluster_ano = reduce(lambda  left,right: pd.merge(left,right,on=['CLUSTER ENGAJAMENTO'],how='outer'), data_frames)

    #pivotando e alterando a ordem
    cluster_ano = pd.melt(cluster_ano,id_vars=['CLUSTER ENGAJAMENTO'],value_vars=cluster_ano.columns.to_list(), var_name='Ano', value_name='percent')
    cluster_ano = cluster_ano.sort_values(by=['Ano'], ascending = True)

    #gráfico
    fig_cluster_ano = px.bar(
        cluster_ano,
        y="Ano",
        x="percent",
        text = "percent",
        color = 'CLUSTER ENGAJAMENTO',
        color_discrete_map = {'Desligar':'#EE2D67','Intervir':'#EBEA70','Orientar':'#002561','Desafiar':'#8EC6B2'},
        category_orders={'Ano':['2020','2021','2022','2023']},
        template = template_dash,
        orientation='h'
    )

    fig_cluster_ano.update_traces(texttemplate='%{x}%', textposition='inside',textfont_size=11, textangle=0, insidetextanchor = 'middle')

    fig_cluster_ano.update_layout(
        xaxis_title="% Porcentagem",
        yaxis_title="Ano",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> % CLUSTER POR ANO YOY* </b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="right",
            x=0.75
        )
    )

    ##Porcentagem de Clusterização por Série

    cluster_serie = df_selection.groupby(by=['Serie','CLUSTER ENGAJAMENTO']).size().reset_index()
    cluster_serie['percent']=df_selection.groupby(by=['Serie','CLUSTER ENGAJAMENTO']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    cluster_serie['percent']=round(cluster_serie['percent']).astype(int)

    fig_cluster_serie = px.bar(
        cluster_serie,
        y="Serie",
        x="percent",
        text = "percent",
        color = 'CLUSTER ENGAJAMENTO',
        color_discrete_map = {'Desligar':'#EE2D67','Intervir':'#EBEA70','Orientar':'#002561','Desafiar':'#8EC6B2'},
        category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
        orientation='h',
        template = template_dash
    )

    fig_cluster_serie.update_traces(texttemplate='%{x}%', textposition='inside',textfont_size=11, textangle=0, insidetextanchor = 'middle')

    fig_cluster_serie.update_layout(
        xaxis_title="% Porcentagem",
        yaxis_title="Série",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> % CLUSTER POR SÉRIE </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="right",
            x=1
        )
    )

    ##Porcentagem de Clusterização por Praça

    cluster_praca = df_selection.groupby(by=['Praça','CLUSTER ENGAJAMENTO']).size().reset_index()
    cluster_praca['percent'] = df_selection.groupby(by=['Praça','CLUSTER ENGAJAMENTO']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    cluster_praca['percent'] = round(cluster_praca['percent']).astype(int)

    fig_cluster_praca = px.bar(
            cluster_praca,
            x='percent',
            y='Praça',
            color = 'CLUSTER ENGAJAMENTO',
            color_discrete_map = {'Desligar':'#EE2D67','Intervir':'#EBEA70','Orientar':'#002561','Desafiar':'#8EC6B2'},
            text = 'percent',
            orientation = 'h',
            template = template_dash
    )

    fig_cluster_praca.update_traces(texttemplate='%{x}%', textposition='inside',
                                    insidetextanchor = 'middle', textfont_size=11, textangle=0)

    fig_cluster_praca.update_layout(
        xaxis_title="% Porcentagem",
        yaxis_title="Praça",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> % CLUSTER POR PRAÇA </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="right",
            x=1
        )
    )

    ##___ENGAJAMENTO ANO X ANO___##

    ## Engajamento ano por série

    #construindo o pivot table com todos os anos
    #ano corrente
    engajamento_60_hj = df_selection.groupby(by=['Serie','ALUNO ALTO ENGAJAMENTO?']).size().reset_index()
    engajamento_60_hj[ano_hoje]=df_selection.groupby(by=['Serie','ALUNO ALTO ENGAJAMENTO?']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    engajamento_60_hj[ano_hoje]=round(engajamento_60_hj[ano_hoje]).astype(int)
    engajamento_60_hj = engajamento_60_hj[engajamento_60_hj['ALUNO ALTO ENGAJAMENTO?'] == "SIM"][["Serie",ano_hoje]]

    #2021
    engajamento_60_2021 = df_2021.groupby(by=['Serie','ALTO ENGAJAMENTO MÉDIA']).size().reset_index()
    engajamento_60_2021['2021']=df_2021.groupby(by=['Serie','ALTO ENGAJAMENTO MÉDIA']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    engajamento_60_2021['2021']=round(engajamento_60_2021['2021']).astype(int)
    engajamento_60_2021 = engajamento_60_2021[engajamento_60_2021['ALTO ENGAJAMENTO MÉDIA'] == "SIM"][["Serie","2021"]]

    #2020
    engajamento_60_2020 = df_2020.groupby(by=['Serie','ALTO ENGAJAMENTO MÉDIA']).size().reset_index()
    engajamento_60_2020['2020']=df_2020.groupby(by=['Serie','ALTO ENGAJAMENTO MÉDIA']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    engajamento_60_2020['2020']=round(engajamento_60_2020['2020']).astype(int)
    engajamento_60_2020 = engajamento_60_2020[engajamento_60_2020['ALTO ENGAJAMENTO MÉDIA'] == "SIM"][["Serie","2020"]]

    #2022
    engajamento_60_2022 = df_2022.groupby(by=['Serie','ALTO ENGAJAMENTO MÉDIA']).size().reset_index()
    engajamento_60_2022['2022']=df_2022.groupby(by=['Serie','ALTO ENGAJAMENTO MÉDIA']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    engajamento_60_2022['2022']=round(engajamento_60_2022['2022']).astype(int)
    engajamento_60_2022 = engajamento_60_2022[engajamento_60_2022['ALTO ENGAJAMENTO MÉDIA'] == "SIM"][["Serie","2022"]]

    #juntando todas as tabelas
    data_frames = [engajamento_60_hj, engajamento_60_2021, engajamento_60_2020,engajamento_60_2022]
    engaj_ano_serie = reduce(lambda  left,right: pd.merge(left,right,on=['Serie'],how='outer'), data_frames)

    #pivotando e alterando a ordem
    engaj_ano_serie = pd.melt(engaj_ano_serie,id_vars=['Serie'],value_vars=engaj_ano_serie.columns.to_list(), var_name='Ano', value_name='percent')
    engaj_ano_serie = engaj_ano_serie.sort_values(by=['Ano'], ascending = True)

    ## Engajamento ano por disciplina

    cols_ano = ['Linguagens','Matemática','Missões','Redação']
    cols_ano_dispensa = ['Missões','Redação']

    if df_selection[df_selection['É liberado de Matemática ou Linguagens?'] == 'Não dispensado'].empty:
        #2023 - ano atual
        df_hj_caderno = df_selection[['ALUNO ALTO ENGAJ MISSÃO?',
                                    'ALUNO ALTO ENGAJ RED?']]
        df_hj_caderno = df_hj_caderno.rename(columns = {'ALUNO ALTO ENGAJ MISSÃO?':'Missões',
                                                        'ALUNO ALTO ENGAJ RED?':'Redação'})
        df_hj_caderno = pd.melt(df_hj_caderno, value_vars=cols_ano_dispensa, var_name='Disciplina', value_name='Alto engajamento')
        df_hj_caderno = df_hj_caderno[df_hj_caderno['Alto engajamento'] !='-']
        engajamento_caderno_hj = df_hj_caderno.groupby(by=['Disciplina','Alto engajamento']).size().reset_index()
        engajamento_caderno_hj[ano_hoje] = df_hj_caderno.groupby(by=['Disciplina','Alto engajamento']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
        engajamento_caderno_hj[ano_hoje]=round(engajamento_caderno_hj[ano_hoje]).astype(int)
        engajamento_caderno_hj = engajamento_caderno_hj[engajamento_caderno_hj['Alto engajamento'] == "SIM"][['Disciplina',ano_hoje]]
        engajamento_caderno_hj.loc[len(engajamento_caderno_hj)] = {'Disciplina': 'Formações (Média das presenças)', '2023': round(presenca_form)} #inserindo a linha de formações que é calculada diferente
        #cálculo do total de engajamento
        engajamento_caderno_hj_total = pd.DataFrame({'Disciplina':['Total'],
                                                    '2023':[round(alto_engaj)]}) #mesmo cálculo do número na parte superior do dashonline
        frames_cad = [engajamento_caderno_hj_total,engajamento_caderno_hj]
        engajamento_caderno_hj = pd.concat(frames_cad)
    else:
        #2023 - ano atual
        df_hj_caderno = df_selection[['ALUNO ALTO ENGAJ LI?',
                                    'ALUNO ALTO ENGAJ MA?',
                                    'ALUNO ALTO ENGAJ MISSÃO?',
                                    'ALUNO ALTO ENGAJ RED?']]
        df_hj_caderno = df_hj_caderno.rename(columns = {'ALUNO ALTO ENGAJ LI?':'Linguagens',
                                                        'ALUNO ALTO ENGAJ MA?':'Matemática',
                                                        'ALUNO ALTO ENGAJ MISSÃO?':'Missões',
                                                        'ALUNO ALTO ENGAJ RED?':'Redação'})
        df_hj_caderno = pd.melt(df_hj_caderno, value_vars=cols_ano, var_name='Disciplina', value_name='Alto engajamento')
        df_hj_caderno = df_hj_caderno[df_hj_caderno['Alto engajamento'] !='-']
        engajamento_caderno_hj = df_hj_caderno.groupby(by=['Disciplina','Alto engajamento']).size().reset_index()
        engajamento_caderno_hj[ano_hoje] = df_hj_caderno.groupby(by=['Disciplina','Alto engajamento']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
        engajamento_caderno_hj[ano_hoje]=round(engajamento_caderno_hj[ano_hoje]).astype(int)
        engajamento_caderno_hj = engajamento_caderno_hj[engajamento_caderno_hj['Alto engajamento'] == "SIM"][['Disciplina',ano_hoje]]
        engajamento_caderno_hj.loc[len(engajamento_caderno_hj)] = {'Disciplina': 'Formações (Média das presenças)', '2023': round(presenca_form)} #inserindo a linha de formações que é calculada diferente
        #cálculo do total de engajamento
        engajamento_caderno_hj_total = pd.DataFrame({'Disciplina':['Total'],
                                                    '2023':[round(alto_engaj)]}) #mesmo cálculo do número na parte superior do dashonline
        frames_cad = [engajamento_caderno_hj_total,engajamento_caderno_hj]
        engajamento_caderno_hj = pd.concat(frames_cad)


    #2021
    df_2021_caderno = df_2021[cols_ano]
    df_2021_caderno = pd.melt(df_2021_caderno, value_vars=cols_ano, var_name='Disciplina', value_name='Alto engajamento')
    df_2021_caderno = df_2021_caderno[df_2021_caderno['Alto engajamento'] != "-"]
    engajamento_caderno_2021 = df_2021_caderno.groupby(by=['Disciplina','Alto engajamento']).size().reset_index()
    engajamento_caderno_2021['2021']=df_2021_caderno.groupby(by=['Disciplina','Alto engajamento']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    engajamento_caderno_2021['2021']=round(engajamento_caderno_2021['2021']).astype(int)
    engajamento_caderno_2021 = engajamento_caderno_2021[engajamento_caderno_2021['Alto engajamento'] == "SIM"][['Disciplina',"2021"]]
    #cálculo do total de engajamento
    total = round(engajamento_caderno_2021['2021'].mean(axis=0))
    engajamento_caderno_2021_total = pd.DataFrame({'Disciplina':['Total'],
                                                '2021':[total]})
    #merge do total com as outras disciplinas
    frames_cad = [engajamento_caderno_2021_total,engajamento_caderno_2021]
    engajamento_caderno_2021 = pd.concat(frames_cad)

    #2020
    df_2020_caderno = df_2020[cols_ano]
    df_2020_caderno = pd.melt(df_2020_caderno, value_vars=cols_ano, var_name='Disciplina', value_name='Alto engajamento')
    df_2020_caderno = df_2020_caderno[df_2020_caderno['Alto engajamento'] != "-"]
    engajamento_caderno_2020 = df_2020_caderno.groupby(by=['Disciplina','Alto engajamento']).size().reset_index()
    engajamento_caderno_2020['2020']=df_2020_caderno.groupby(by=['Disciplina','Alto engajamento']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    engajamento_caderno_2020['2020']=round(engajamento_caderno_2020['2020']).astype(int)
    engajamento_caderno_2020 = engajamento_caderno_2020[engajamento_caderno_2020['Alto engajamento'] == "SIM"][['Disciplina',"2020"]]
    #cálculo do total de engajamento
    total = round(engajamento_caderno_2020['2020'].mean(axis=0))
    engajamento_caderno_2020_total = pd.DataFrame({'Disciplina':['Total'],
                                                '2020':[total]})
    #merge do total com as outras disciplinas
    frames_cad = [engajamento_caderno_2020_total,engajamento_caderno_2020]
    engajamento_caderno_2020 = pd.concat(frames_cad)

    #2022
    df_2022_caderno = df_2022[cols_ano]
    df_2022_caderno = pd.melt(df_2022_caderno, value_vars=cols_ano, var_name='Disciplina', value_name='Alto engajamento')
    df_2022_caderno = df_2022_caderno[df_2022_caderno['Alto engajamento'] != "-"]
    engajamento_caderno_2022 = df_2022_caderno.groupby(by=['Disciplina','Alto engajamento']).size().reset_index()
    engajamento_caderno_2022['2022']=df_2022_caderno.groupby(by=['Disciplina','Alto engajamento']).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    engajamento_caderno_2022['2022']=round(engajamento_caderno_2022['2022']).astype(int)
    engajamento_caderno_2022 = engajamento_caderno_2022[engajamento_caderno_2022['Alto engajamento'] == "SIM"][['Disciplina',"2022"]]
    #cálculo das formações: média das formações
    df_2022_form = round(np.nanmean(df_2022['Presença Média'])*100) #LINHAS 711 E 712 COMENTADAS - 03/05 - GABRIEL LIMA
    engajamento_caderno_2022.loc[len(engajamento_caderno_2022)] = {'Disciplina': 'Formações (Média das presenças)', '2022': df_2022_form} #inserindo a linha de formações que é calculada diferente

    #cálculo do total de engajamento
    total = round(engajamento_caderno_2022['2022'].mean(axis=0))
    engajamento_caderno_2022_total = pd.DataFrame({'Disciplina':['Total'],
                                                '2022':[total]})
    #merge do total com as outras disciplinas
    frames_cad = [engajamento_caderno_2022_total,engajamento_caderno_2022]
    engajamento_caderno_2022 = pd.concat(frames_cad)

    #juntando todas as tabelas
    data_frames = [engajamento_caderno_hj, engajamento_caderno_2021, engajamento_caderno_2020,engajamento_caderno_2022]
    engaj_ano_caderno = reduce(lambda  left,right: pd.merge(left,right,on=['Disciplina'],how='outer'), data_frames)

    #pivotando e alterando a ordem
    engaj_ano_caderno = pd.melt(engaj_ano_caderno,id_vars=['Disciplina'],value_vars=engaj_ano_caderno.columns.to_list(), var_name='Ano', value_name='percent')
    engaj_ano_caderno = engaj_ano_caderno.sort_values(by=['Ano'], ascending = True)

    #gráfico de engajamento por disciplina/caderno
    fig_engaj_ano_caderno = px.bar(
        engaj_ano_caderno,
        x="Disciplina",
        y="percent",
        text = "percent",
        color = "Ano",
        category_orders={'Disciplina':['Linguagens','Matemática','Missões','Redação','Formações (Média das presenças)','Total']},
        template = template_dash,
        color_discrete_sequence= colors,
        barmode='group'
    )

    fig_engaj_ano_caderno.update_layout(
        showlegend=True,
        xaxis_title="Disciplina",
        yaxis_title="% Porcentagem",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> % ALUNOS ENGAJAMENTO ACIMA DE 60%: DISCIPLINA* </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    fig_engaj_ano_caderno.update_yaxes(visible=False)

    ##Engajamento mês a mês YoY [[AJUSTAR]]
    #atualmente está com o cálculo da meta de 2022, 2023 é diferente


    #2022
    #engajamento por disciplina

    #abaixo para o cálculo de 2022, realiza-se a média de cada uma das disciplinas e depois a média entre todas as colunas
    def dataframe_meta(df,col):
        #retirar os dispensados
        df = df[(df[col] != '-') & (df['Status'] == 'ATIVO')]

        #pivot_table de alto engajamento
        pivot_table_col = pd.pivot_table(df,
                                        values = 'ID',
                                        index = 'Mês',
                                        columns= col,
                                        aggfunc='count',
                                        margins=True,
                                        margins_name='Total').pipe(lambda d:(round(d.div(d['Total'], axis='index')*100,0)))

        pivot_table_col = pivot_table_col[['SIM']]
        pivot_table_col.rename(columns={'SIM': col},inplace = True)

        return pivot_table_col

    def join_diferentes_discip(df):
        engajamento_li = dataframe_meta(df,'Linguagens')
        engajamento_ma = dataframe_meta(df,'Matemática')
        engajamento_miss = dataframe_meta(df,'Missões')
        engajamento_red = dataframe_meta(df,'Redação')

        frames = [engajamento_li,engajamento_ma,engajamento_miss,engajamento_red]
        engajamento_meta = reduce(lambda  left,right: pd.merge(left,right,on=['Mês'],how='outer'), frames)

        engajamento_meta['Média Engajamento'] = round(engajamento_meta.mean(axis=1))

        return engajamento_meta

    engajamento_hist_22 = join_diferentes_discip(df_2022_yoy)[['Média Engajamento']]
    engajamento_hist_22.rename(columns = {'Média Engajamento':'2022'},inplace=True)

    engajamento_hist_21 = join_diferentes_discip(df_2021_yoy)[['Média Engajamento']]
    engajamento_hist_21.rename(columns = {'Média Engajamento':'2021'},inplace=True)

    engajamento_hist_20 = join_diferentes_discip(df_2020_yoy)[['Média Engajamento']]
    engajamento_hist_20.rename(columns = {'Média Engajamento':'2020'},inplace=True)

    #juntando todas as tabelas
    data_frames = [engajamento_hist_22, engajamento_hist_21, engajamento_hist_20]
    engaj_yoy = reduce(lambda  left,right: pd.merge(left,right,on=['Mês'],how='outer'), data_frames)
    engaj_yoy = engaj_yoy.drop('Total').reset_index()

    #pivotando e alterando a ordem
    engaj_yoy = pd.melt(engaj_yoy,id_vars=['Mês'],value_vars=engaj_yoy.columns.to_list(), var_name='Ano', value_name='percent')
    engaj_yoy = engaj_yoy.sort_values(by=['Ano'], ascending = True)

    #gráfico de engajamento por mês Yoy
    fig_engaj_yoy = px.bar(
        engaj_yoy,
        x="Mês",
        y="percent",
        text = "percent",
        color = "Ano",
        category_orders={'Mês':['Abril','Maio','Junho','Julho','Agosto', 'Setembro', 'Outubro', 'Novembro','Dezembro']},
        template = template_dash,
        color_discrete_map= {'2020':'#EBEA70','2021':'#002561', '2022':'#8EC6B2'},
        barmode='group'
    )

    fig_engaj_yoy.update_layout(
        showlegend=True,
        xaxis_title="Mês",
        yaxis_title="% Porcentagem",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> MÉDIA DE ALTO ENGAJAMENTO: MÊS A MÊS* </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    fig_engaj_yoy.update_yaxes(visible=False)

    #### ----- Layout dos gráficos na tela
    espaco1,espaco2=st.columns(2)
    #----- primeira  linha----
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig_status, use_container_width=True)
    with col2:
        st.plotly_chart(fig_quant_serie,use_container_width=True)

    #----- segunda  linha----
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig_quant_praca,use_container_width=True)
    with col2:
        st.plotly_chart(fig_tipo_serie,use_container_width=True)

    st.markdown("---")
    #título da próxima seção de engajamento
    st.markdown("<h3 style= 'text-align: center'> Engajamento </h3>", unsafe_allow_html=True)

    #----- terceira linha -----
    container=st.container()
    with container:
        st.plotly_chart(fig_engaj_ano_caderno,use_container_width=True)

     #----- quarta linha -----
    container=st.container()
    with container:
        st.plotly_chart(fig_engaj_yoy,use_container_width=True)

    #----- quinta linha -----

    #slider com as disciplinas para selecionar
    if df_selection[df_selection['É liberado de Matemática ou Linguagens?'] == 'Não dispensado'].empty:
        slider = st.select_slider('Selecione a disciplina', options=['Missões','Redação'])
    else:
        slider = st.select_slider('Selecione a disciplina', options=['Matemática','Linguagens','Missões','Redação'])
    if slider == 'Matemática':
        disciplina = 'ALUNO ALTO ENGAJ MA?'
        meta_disciplina = 83
    elif slider == 'Linguagens':
        disciplina = 'ALUNO ALTO ENGAJ LI?'
        meta_disciplina = 83
    elif slider == 'Missões':
        disciplina = 'ALUNO ALTO ENGAJ MISSÃO?'
        meta_disciplina = 83
    elif slider == 'Redação':
        disciplina = 'ALUNO ALTO ENGAJ RED?'
        meta_disciplina = 83

    #gráfico de engajamento por discplina por série
    #esse gráfico depende do input do slider, e, portanto, não poderia ser codado antes do slider

    #2023
    engaj_discip_hj = df_selection.groupby(by=['Serie', disciplina]).size().reset_index()
    engaj_discip_hj = engaj_discip_hj[engaj_discip_hj[disciplina] != '-']
    engaj_discip_hj['quantidade'] = engaj_discip_hj.loc[:,0]
    pivot_discip_hj = pd.pivot_table(engaj_discip_hj,
                                    values = 'quantidade',
                                    index=['Serie'],
                                    columns=[disciplina],
                                    aggfunc='sum',
                                    margins=True,
                                    margins_name='Total').pipe(lambda d:(round(d.div(d['Total'], axis='index')*100,0)))

    pivot_discip_hj['percent']= pivot_discip_hj['SIM']
    pivot_discip_hj['Ano']= ano_hoje
    pivot_discip_hj = pivot_discip_hj[['percent','Ano']].reset_index()

    #2022
    engaj_discip_22 = df_2022.groupby(by=['Serie', slider]).size().reset_index()
    engaj_discip_22 = engaj_discip_22[engaj_discip_22[slider] != '-']
    engaj_discip_22['quantidade'] = engaj_discip_22.loc[:,0]
    pivot_discip_22 = pd.pivot_table(engaj_discip_22,
                                    values = 'quantidade',
                                    index=['Serie'],
                                    columns=[slider],
                                    aggfunc='sum',
                                    margins=True,
                                    margins_name='Total').pipe(lambda d:(round(d.div(d['Total'], axis='index')*100,0)))
    pivot_discip_22['percent']= pivot_discip_22['SIM']
    pivot_discip_22['Ano']= '2022'
    pivot_discip_22 = pivot_discip_22[['percent','Ano']].reset_index()

    #merge 22 e 23
    frames_discp = [pivot_discip_22, pivot_discip_hj]
    engaj_discip = pd.concat(frames_discp)
    engaj_discip.sort_values(by=['Ano'], ascending = True, inplace = True)

    fig_engaj_discip = px.bar(
        engaj_discip,
        x='percent',
        y='Serie',
        text = 'percent',
        color = 'Ano',
        category_orders={'Serie':['Total','8º EF','9º EF','1º EM','2º EM','3º EM']},
        orientation = 'h',
        color_discrete_map= {'2022':'#EBEA70', '2023': '#EE2D67'},
        template = template_dash,
        barmode='group'
    )
    
    fig_engaj_discip.update_layout(
        xaxis_title="% Porcentagem",
        yaxis_title="Série",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> % ALUNOS ENGAJAMENTO ACIMA DE 60%: "+slider+"* </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend={'traceorder': 'reversed'}
    )

    texto_meta = 'Ideal = '+ str(meta_disciplina)

    fig_engaj_discip.update_xaxes(visible=False, showticklabels=False, range=[0, 100])
    fig_engaj_discip.add_vline(x=meta_disciplina,annotation_text=texto_meta)
    st.plotly_chart(fig_engaj_discip,use_container_width=True)
    st.write("*As informações anteriores a 2023 não se alteram com o filtro de Tutores")

    #YoY da presença nas formações

    cols_form = ['Presença 1ªF','Presença 2ªF','Presença 3ªF','Presença 4ªF','Média Formações']

    #2022
    formacao_22 = pd.DataFrame(data = {'Formações': cols_form,
                        '2022': [70,62,64,61,64]})

    #2023calculando a formação do ano atual
    formacoes = [form_1,form_2,form_3,form_4,presenca_form]
    np_array = np.array(formacoes) #arredondar a lista de presenca nas formações
    np_round_to_tenths = np.around(np_array, 0)
    formacoes_arredondado = list(np_round_to_tenths)
    #montando tabela 2023
    formacao_hj = pd.DataFrame(data = {'Formações': cols_form,
                        '2023': formacoes_arredondado})

    #merge 22 e 23
    formacao_hist= formacao_22.merge(formacao_hj, left_on='Formações', right_on='Formações')

    formacao_hist = pd.melt(formacao_hist,id_vars=['Formações'],value_vars=[ano_hoje,'2022'], var_name='Ano', value_name='Presença')
    formacao_hist = formacao_hist.sort_values(by=['Ano'], ascending = True)

    #gráfico de formações
    fig_formacao_hist = px.bar(
        formacao_hist,
        x="Formações",
        y="Presença",
        text = "Presença",
        color = "Ano",
        category_orders={'Formações':cols_form},
        template = template_dash,
        color_discrete_map= {'2019':'#EE2D67', '2023':'#8EC6B2'},
        color_discrete_sequence= colors,
        barmode='group'
    )

    fig_formacao_hist.update_layout(
        showlegend=True,
        xaxis_title="Formações",
        yaxis_title="Presença",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> % PRESENÇA NAS FORMAÇÕES (CÁLCULO DA META)** </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    fig_formacao_hist.update_traces(texttemplate='%{y}%', textposition='inside',textfont_size=15)

    fig_formacao_hist.update_yaxes(visible=False)
    
    st.plotly_chart(fig_formacao_hist,use_container_width=True)
    st.write("**Meta de formações = % de presença dos alunos nas formações na época das formações.")

    #----- sexta linha----
    st.plotly_chart(fig_cluster_ano, use_container_width=True)
    st.write("*As informações anteriores a 2023 não se alteram com o filtro de Tutores")

    #----- sétima linha---
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig_cluster_serie, use_container_width=True)
    with col2:
        st.plotly_chart(fig_cluster_praca,use_container_width=True)

    #inserir tab de engajamento geral a posteriori
    ####### TABS
    tab1,tab2, tab3,tab4,tab5= st.tabs(['Prova Única','Teste Olimpiadas','Olimpíadas','Acompanhamento Quinzenal', 'Khan Academy' ])
    with tab1:
        col1,col2=st.columns(2,gap='small')
        with col1:
            pu_boxplot = df_dash2022[['Serie',' MÉDIA ENEM PROJETADO',' MÉDIA ENEM PROJETADO PU 2']].round()

            fig_pu1_boxplot = px.box(
                pu_boxplot,
                x="Serie",
                y=' MÉDIA ENEM PROJETADO',
                category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
                template = template_dash,
                color_discrete_sequence= ['#002561']
            )

            fig_pu1_boxplot.update_layout(
                xaxis_title="Série",
                yaxis_title="Média ENEM Projetado",
                plot_bgcolor=bg_color_dash,
                title={
                    'text': "<b> DISTRIBUIÇÃO ENEM PROJETADA PU 1 </b>",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )

            fig_pu1_boxplot.update_yaxes(range=[100, 900])

            fig_pu1_boxplot.update_traces(boxmean = True)

            st.plotly_chart(fig_pu1_boxplot,use_container_width=True)

        with col2:
            fig_pu2_boxplot = px.box(
                pu_boxplot,
                x="Serie",
                y=' MÉDIA ENEM PROJETADO PU 2',
                category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
                template = template_dash,
                color_discrete_sequence= ['#8EC6B2']
            )

            fig_pu2_boxplot.update_layout(
                xaxis_title="Série",
                yaxis_title="Média ENEM Projetado",
                plot_bgcolor=bg_color_dash,
                title={
                    'text': "<b> DISTRIBUIÇÃO ENEM PROJETADA PU 2 </b>",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )

            fig_pu2_boxplot.update_traces(boxmean = True)

            fig_pu2_boxplot.update_yaxes(range=[100, 900])

            st.plotly_chart(fig_pu2_boxplot,use_container_width=True)
        ##----- segunda linha -----
        #gráfico de médias da PU ano a ano
        #imputando os valores de 2021
        notas = {'Serie': ['8º EF','9º EF','1º EM','2º EM','3º EM'],
                        '2021 PU 1': [577,622,666,672,673],
                        '2021 PU 2': [610.0853187,613.8771636,659.3912762,661.5257525,647.1816498]
                        }

        notas_pu_2021 = pd.DataFrame(data=notas).round()

        #calculando 2022

        media_2022 = df_dash2022[['Serie',' MÉDIA ENEM PROJETADO',' MÉDIA ENEM PROJETADO PU 2']].groupby(by=['Serie']).mean().reset_index() #LIMITANDO O DF_DASH2022 PARA SERIE, MEDIA ENEM PROJETADO E MEDIA ENEM PROJETADO PU 2 - 03/05 - GABRIEL LIMA
        pu_2022_enemp = media_2022[['Serie',' MÉDIA ENEM PROJETADO',' MÉDIA ENEM PROJETADO PU 2']].round()
        pu_2022_enemp = pu_2022_enemp.rename(columns = {' MÉDIA ENEM PROJETADO': '2022 PU 1',
                                        ' MÉDIA ENEM PROJETADO PU 2':'2022 PU 2'})
        pus = [pu_2022_enemp, notas_pu_2021]
        pu_enemp = reduce(lambda left,right: pd.merge(left,right,on=['Serie'],how='outer'), pus)

        #pivotando e alterando a ordem
        pu_enemp = pd.melt(pu_enemp,id_vars=['Serie'],value_vars=pu_enemp.columns.tolist(), var_name='PU', value_name='Média ENEM Projetado')
        pu_enemp = pu_enemp.sort_values(by=['PU'], ascending = True)

        #Separando PU 1 e PU 2
        pu_1_enemp = pu_enemp[(pu_enemp['PU'] == "2021 PU 1") | (pu_enemp['PU'] == "2022 PU 1")]

        #gráfico PU 1
        fig_pu_1_enemp = px.bar(
            pu_1_enemp,
            x="Serie",
            y="Média ENEM Projetado",
            text = "Média ENEM Projetado",
            color = "PU",
            category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
            template = template_dash,
            color_discrete_map={'2021 PU 1':'#002561', '2022 PU 1':'#8EC6B2'},
            barmode='group'
        )

        fig_pu_1_enemp.update_layout(
            showlegend=True,
            xaxis_title="Série",
            yaxis_title="Média ENEM Projetado",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> MÉDIA ENEM PROJETADA YoY - PU 1 2022</b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_pu_1_enemp.update_yaxes(visible=False)

        st.plotly_chart(fig_pu_1_enemp,use_container_width=True)

        #df PU 2
        pu_2_enemp = pu_enemp[(pu_enemp['PU'] == "2021 PU 2") | (pu_enemp['PU'] == "2022 PU 2")]

        #gráfico PU 2
        fig_pu_2_enemp = px.bar(
            pu_2_enemp,
            x="Serie",
            y="Média ENEM Projetado",
            text = "Média ENEM Projetado",
            color = "PU",
            category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
            template = template_dash,
            color_discrete_map={'2021 PU 2':'#002561', '2022 PU 2':'#8EC6B2'},
            barmode='group'
        )

        fig_pu_2_enemp.update_layout(
            showlegend=True,
            xaxis_title="Série",
            yaxis_title="Média ENEM Projetado",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> MÉDIA ENEM PROJETADA YoY - PU 2 2022 </b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_pu_2_enemp.update_yaxes(visible=False)

        st.plotly_chart(fig_pu_2_enemp,use_container_width=True)
    with tab2:
        st.write('Por padrão os dados abaixo consideram o ano de 2022 e 2023, caso queira analisar cada ano específicamente basta fazer o filtro abaixo.')
        st.write('Vale ressaltar que quanto aos dados de 2022 estamos falando de alunos ativos na época, ou seja vai aparecer dados de alunos ativos em dezembro de 2022 que foram desligados durante 2023 por exemplo.')

        col1,espaco1,col2 = st.columns([1,1,1])

        medalhistas_unicos = df_selection_olimp_teste[(df_selection_olimp_teste['Medalhas acadêmicas'] != "")]
        medalhistas_unicos = medalhistas_unicos.drop_duplicates(['ID'])


        tabela_medalhistas_serie=  medalhistas_unicos.groupby('Selecione a sua série:')['Ano'].value_counts().unstack(fill_value=0)
        tabela_medalhistas_serie = tabela_medalhistas_serie.rename_axis(None, axis=1)
        tabela_medalhistas_serie = tabela_medalhistas_serie.reset_index()

        fig_olimp_medalhistas = px.bar(
            tabela_medalhistas_serie,
            x='Selecione a sua série:', 
            y=[2022, 2023],     
            color_discrete_map= {'2022':'#EE2D67', '2023':'#8EC6B2'},
            barmode='group',
            category_orders={'Selecione a sua série:':cols_form},
            template = template_dash)

        fig_olimp_medalhistas.update_layout(
            showlegend=True,
            xaxis_title="Série",
            yaxis_title="Medalhistas",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> QUANTIDADE DE ALUNOS MEDALHISTAS POR SÉRIE EM CADA ANO </b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_olimp_medalhistas.update_yaxes(visible=False)

        st.plotly_chart(fig_olimp_medalhistas,use_container_width=True)

    with tab3:

        df_alunos_medalhas = df_selection.loc[(df_selection['Me inscrevi e estou aguardando resultados'].notnull() & (df_selection['Me inscrevi e estou aguardando resultados'] != 0)& (df_selection['Me inscrevi e estou aguardando resultados'] != "-")) 
                                              | (df_selection['Medalhas acadêmicas'].notnull() & (df_selection['Medalhas acadêmicas'] != "0") & (df_selection['Medalhas acadêmicas'] != "-"))]

        alunos_medalhas = df_alunos_medalhas.groupby(by=['Serie']).size().reset_index()
        alunos_medalhas['quantidade'] = alunos_medalhas.loc[:,0]
        alunos_medalhas = pd.DataFrame(alunos_medalhas)

        #contando quantos alunos ativos tem por série
        cont_alunos = df_dash360_ativo.groupby(by=['Serie']).count()['ID']
        cont_alunos = pd.DataFrame(cont_alunos)

        #ordenar as séries
        order_serie = df_selection[['ordem_serie','Serie']].groupby(by=['ordem_serie','Serie']).mean().reset_index() #limitando o df_selection a ordem serie e serie - 03/05 - GABRIEL LIMA
        order_serie = order_serie[['ordem_serie','Serie']]

        #mesclando as duas tabelas para fazer a coluna % Série
        medalhas_serie_unique = alunos_medalhas.merge(cont_alunos, left_on='Serie', right_on='Serie')
        medalhas_serie_unique = medalhas_serie_unique.merge(order_serie, left_on='Serie', right_on='Serie')
        medalhas_serie_unique['% Serie'] = ((medalhas_serie_unique['quantidade']/medalhas_serie_unique['ID'])*100).round().astype(int)
        medalhas_serie_unique = medalhas_serie_unique.sort_values(by=['ordem_serie'])

        # st metric d e
        col1,col2=st.columns(2,gap='small')
        ### segunda linha
        with col1:
            st.metric(label="Total de estudantes com alguma medalha ou inscrição",
                    value=str(sum(medalhas_serie_unique['quantidade'])),
                    help = "Estudantes únicos com pelo menos uma medalha e/ou inscrição")


            fig_medalhas_serie_unique = px.bar(
                medalhas_serie_unique,
                x="Serie",
                y='quantidade',
                text = 'quantidade',
                color = "Serie",
                category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
                template = template_dash,
                color_discrete_sequence=colors
            )

            fig_medalhas_serie_unique.update_layout(
                showlegend=False,
                xaxis_title="Série",
                yaxis_title="# Quantidade",
                plot_bgcolor=bg_color_dash,
                title={
                    'text': "<b> # ESTUDANTES ÚNICOS COM MEDALHA POR SÉRIE </b>",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )

            fig_medalhas_serie_unique.update_yaxes(visible=False, showticklabels=False)

            st.plotly_chart(fig_medalhas_serie_unique,use_container_width=True)
        with col2:

            st.metric(label="Total de estudantes com alguma medalha",
                    value=len(df_selection.loc[(df_selection['Medalhas acadêmicas'].notnull())]['Medalhas acadêmicas']),
                    help = "Estudantes únicos com pelo menos uma medalha")

            fig_medalhas_serie_pct = px.line(
                medalhas_serie_unique,
                x="Serie",
                y="% Serie",
                text = 'quantidade',
                category_orders={'Serie':['8º EF','9º EF','1º EM','2º EM','3º EM']},
                template = template_dash,
                color_discrete_sequence=colors
            )

            fig_medalhas_serie_pct.update_traces(texttemplate='%{y}%', textposition='top center',textfont_size=15)

            fig_medalhas_serie_pct.update_layout(
                showlegend=False,
                xaxis_title="Série",
                yaxis_title="Percentual em relação ao total da série",
                plot_bgcolor=bg_color_dash,
                title={
                    'text': "<b> % DA SÉRIE COM ALGUMA MEDALHA/INSCRIÇÃO </b>",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )

            fig_medalhas_serie_pct.update_xaxes(showgrid=False)

            #fig_medalhas_serie_pct.update_yaxes(showgrid=False)

            st.plotly_chart(fig_medalhas_serie_pct,use_container_width=True)
        ## ----- segunda linha
        medalha_competicao = df_olimp.groupby(by=['Olimpíada', 'Status da Inscrição']).size().reset_index()
        medalha_competicao['quantidade'] = medalha_competicao.loc[:,0]
        medalha_competicao = medalha_competicao.sort_values(['quantidade'],ascending=False)

        fig_medalha_competicao = px.bar(
                medalha_competicao,
                y="Olimpíada",
                x="quantidade",
                text = "quantidade",
                color = "Status da Inscrição",
                color_discrete_sequence = colors,
                template = template_dash,
                barmode='stack',
                orientation = 'h',
                height = 600
            )

        fig_medalha_competicao.update_traces(texttemplate='%{x}',
            textposition='inside',
            textfont_size=11,
            insidetextanchor = 'middle')

        fig_medalha_competicao.update_yaxes(tickangle=0) #tickfont=dict(size=9),)

        fig_medalha_competicao.update_xaxes(visible=False)

        fig_medalha_competicao.update_layout(yaxis=dict(autorange="reversed"), legend=dict(
            xanchor="right",
            x=0.99,
            yanchor="top",
            y=0.55
            ))


        fig_medalha_competicao.update_layout(
            plot_bgcolor=bg_color_dash,
            title={
            'text': "<b> STATUS DE INSCRIÇÃO POR OLIMPÍADA </b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
            }
            )
        st.plotly_chart(fig_medalha_competicao,use_container_width=True)

    with tab4:

        #quantidade de contato com os alunos
        tutor_quinz = df_quinzenal[['Tutor','Quantidade de contatos']].groupby(by=['Tutor']).sum().reset_index()
        tutor_quinz = pd.DataFrame(data=tutor_quinz)

        #% de foco da quinzena realizado
        #(fómula interna da planilha) nesse caso, se o aluno estava no foco e foi contatado = 1; se estava no foco e não foi contatado = 0
        quinzenal_foco = df_quinzenal.dropna(subset=['Tema prioritário'])
        quinzenal_foco = quinzenal_foco[['Tutor','Foco']].groupby(by=['Tutor']).mean().reset_index()
        quinzenal_foco['Foco'] = round(100*quinzenal_foco['Foco']).astype(int)
        quinzenal_foco = pd.DataFrame(data=quinzenal_foco)

        #merge
        tutor_quinz = tutor_quinz.merge(quinzenal_foco, left_on='Tutor', right_on='Tutor')

        fig_tutor_quinz_pct = px.line(
            tutor_quinz,
            x="Tutor",
            y="Foco",
            text = "Foco",
            template = template_dash,
            color_discrete_sequence=colors
        )

        fig_tutor_quinz_pct.update_traces(texttemplate='%{y}%', textposition='top center',textfont_size=15)

        fig_tutor_quinz_pct.update_layout(
            showlegend=False,
            xaxis_title="Tutor",
            yaxis_title="Percentual de focos da quinzena realizados",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> % DO FOCO REALIZADO PELO TUTOR </b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_tutor_quinz_pct.update_xaxes(showgrid=False)
        st.plotly_chart(fig_tutor_quinz_pct,use_container_width=True)

        fig_tutor_quinz = px.bar(
            tutor_quinz,
            x="Tutor",
            y='Quantidade de contatos',
            text = 'Quantidade de contatos',
            color = "Tutor",
            template = template_dash,
            color_discrete_sequence=colors
        )

        fig_tutor_quinz.update_layout(
            showlegend=False,
            xaxis_title="Tutor",
            yaxis_title="Quantidade de contatos",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> CONTATOS POR TUTOR </b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_tutor_quinz.update_yaxes(visible=False, showticklabels=False)

        st.plotly_chart(fig_tutor_quinz,use_container_width=True)

    with tab5:

        st.markdown('O Khan Academy foi uma atividade pontual disponibilizada para os alunos de 8º EF e 9º EF entre Fevereiro e Março de 2023. Portanto, na seleção abaixo você pode escolher os gráficos serem vistos como:')
        st.markdown('**"13/03/2023"** - Da forma como fechou o engajamento/progresso na data de fechamento da atividade (Opção padrão);')
        st.markdown('Ou **"Hoje"** - A partir da base ativa atual, entender qual o percentual de quem ainda está no IOL atualmente que realizou a atividade.')
        st.markdown('Os números diferem entre si de acordo com a base ativa, uma vez que ocorrem desligamentos dos alunos ao longo do ano.')

        col1,espaco1,col2 = st.columns([1,1,1])
        with col1:
            select = st.selectbox(
                "Selecione o tipo de visualização:",
                options=['13/03/2023','Hoje'],
                help = 'Escolha qual base ativa você gostaria de ver os dados abaixo'
                )
            if select == '13/03/2023':
                @st.cache_data
                def importar_dashkhan():
                    df_dash2023khan = pd.read_excel(r"Dash 360 Final_2023_Khan.xlsx")
                    df_dash2023khan = df_dash2023khan[df_dash2023khan['Status'] == 'ATIVO']
                    return df_dash2023khan

                df_base_khan = importar_dashkhan()
            else:
                df_base_khan = df_selection

        ## O khan academy é uma atividade eventual disponibilizada apenas para o 8ºEF e 9º EF no começo de 2023
        ## Portanto, certos filtros (ex.: tutor X que atende apenas 3º EM) irão quebrar todos os gráficos
        ## Nesse sentido, o condicional abaixo permite identificar e barrar a visualização de dados

        if df_selection['8º EF e 9º EF - PROGRESSO KHAN ACADEMY'].isnull().all():
            st.write('Não é possível mostrar engajamento de khan com os filtros atuais. Khan Academy está disponível apenas para alunos de 8º EF e 9º EF')
        else:
            df_khan = df_base_khan[(df_base_khan['Serie'] == '8º EF') | (df_base_khan['Serie'] == '9º EF')]

            #filtro de serie
            col1,espaco1 = st.columns([1,2])
            with col1:
                serie = st.multiselect(
                    "Selecione a série:",
                    options=df_khan['Serie'].dropna().unique(),
                    default=df_khan['Serie'].dropna().unique()
                    )
            ##ver se multiselect = None, then multiselect = default kkk
            ### quando não tem série selecionada daá erro

            df_khan = df_khan.query("Serie == @serie")

            ### % de alunos acima de 50% e % de alunos acima de 80%
            col1, espaco1, col2, espaco2 = st.columns([1,1,1,1])
            with col1:
                khan_mais50 = round(len(df_khan[df_khan['8º EF e 9º EF - PROGRESSO KHAN ACADEMY']>=50])/len(df_khan['8º EF e 9º EF - PROGRESSO KHAN ACADEMY'])*100)
                st.metric(label = "% da base com mais de 50% de progresso",
                        value = khan_mais50,
                        help = "De acordo com os filtros selecionados, essa é a quantidade de estudantes da base com mais de 50% de engajamento dividido pela quantidade toal de estudantes ativos")

            with col2:
                khan_mais80 = round(len(df_khan[df_khan['8º EF e 9º EF - PROGRESSO KHAN ACADEMY']>=80])/len(df_khan['8º EF e 9º EF - PROGRESSO KHAN ACADEMY'])*100)
                st.metric(label = "% da base com mais de 80% de progresso",
                        value = khan_mais80,
                        help = "De acordo com os filtros selecionados, essa é a quantidade de estudantes da base com mais de 80% de engajamento dividido pela quantidade toal de estudantes ativos")

            st.write("Progresso coletado de fevereiro até 12/03 para 9º EF e até 08/03 para 8º EF. Para participar do sorteio dos tablets, foram contabilizados apenas os alunos com +80% de progresso até 08/03 (independente da série).")

            col1,col2 = st.columns([1,1])

            with col1:
                ## gráfico de pizza de engajamento
                df_khan_pct = pd.pivot_table(df_khan,
                                    index = 'KHAN - Classificação',
                                    values = 'Nome',
                                    aggfunc = 'count')

                df_khan_pct['Percentual'] = round(((df_khan_pct['Nome'])/(df_khan_pct['Nome'].sum()))*100)
                fig_khan_pie = px.pie(
                        df_khan_pct,
                        values = 'Percentual',
                        title = "<b> PROGRESSO EM KHAN </b>",
                        names = df_khan_pct.index,
                        color_discrete_sequence = colors,
                        hole = .4,
                        template = template_dash)

                fig_khan_pie.update_traces(textposition='auto',
                                        texttemplate="%{percent:.0%} %{label}",
                                        textfont_size=15,
                                        sort = False)
                fig_khan_pie.update_layout(uniformtext_minsize=12,
                                        title={
                                            'text': "<b> PROGRESSO EM KHAN </b>",
                                            'y':0.9,
                                            'x':0.5,
                                            'xanchor': 'center',
                                            'yanchor': 'top'}
                                        )
                st.plotly_chart(fig_khan_pie,use_container_width=True)

            ## engajamento stacked por tutor(a)
            with col2:
                ## progresso por praca
                df_khan_praca = pd.crosstab(df_khan['KHAN - Classificação'],
                            df_khan['Praça'],
                            values = 'Nome',
                            aggfunc = 'count',
                            normalize='columns').applymap(lambda x: "{0:.0f}".format(100*x)).reset_index()

                df_khan_praca = pd.melt(df_khan_praca,id_vars='KHAN - Classificação',value_vars=df_khan_praca.columns.to_list(), var_name='Praça', value_name='percent')
                df_khan_praca['percent'] = pd.to_numeric(df_khan_praca['percent'])

                fig_khan_praca = px.bar(
                        df_khan_praca,
                        x='percent',
                        y="Praça",
                        text = "percent",
                        title = "<b> PROGRESSO EM KHAN POR PRAÇA </b>",
                        color = 'KHAN - Classificação',
                        color_discrete_sequence = colors,
                        template = template_dash,
                        barmode='stack',
                        orientation = 'h'
                    )
                fig_khan_praca.update_traces(texttemplate='%{x}',
                                            textposition='inside',
                                            textfont_size=11,
                                            textangle=0,
                                            insidetextanchor = 'middle'
                                            )

                fig_khan_praca.update_xaxes(tickfont=dict(size=11))

                fig_khan_praca.update_xaxes(visible=False)

                fig_khan_praca.update_layout(legend=dict(
                                                    orientation="h",
                                                    yanchor="bottom",
                                                    y=-0.25,
                                                    xanchor="right",
                                                    x=0.75))
                st.plotly_chart(fig_khan_praca,use_container_width=True)

            #progresso por tutor
            df_khan_tutor = pd.crosstab(df_khan['KHAN - Classificação'],
                                        df_khan['Tutor'],
                                        values = 'Nome',
                                        aggfunc = 'count',
                                        normalize='columns').applymap(lambda x: "{0:.0f}".format(100*x)).reset_index()

            df_khan_tutor = pd.melt(df_khan_tutor,id_vars='KHAN - Classificação',value_vars=df_khan_tutor.columns.to_list(), var_name='Tutor', value_name='percent')
            df_khan_tutor['percent'] = pd.to_numeric(df_khan_tutor['percent']) # transformando o pct em número para ser processado pelo gráfico

            fig_khan_tutor = px.bar(
                    df_khan_tutor,
                    x='Tutor',
                    y="percent",
                    text = "percent",
                    title = "<b> PROGRESSO EM KHAN POR TUTOR(A) </b>",
                    color = 'KHAN - Classificação',
                    color_discrete_sequence = colors,
                    template = template_dash,
                    barmode='stack'
                )

            fig_khan_tutor.update_xaxes(tickfont=dict(size=11))

            fig_khan_tutor.update_yaxes(visible=False)

            fig_khan_tutor.update_layout(legend=dict(
                                                orientation="h",
                                                yanchor="bottom",
                                                y=-0.25,
                                                xanchor="right",
                                                x=0.75))

            fig_khan_tutor.update_traces(texttemplate='%{y}',
                                        textposition='inside',
                                        textfont_size=11,
                                        textangle=0,
                                        insidetextanchor = 'middle'
                                        )

            st.plotly_chart(fig_khan_tutor,use_container_width=True)

            ## puxar da planilha de acompanhamento
    #with tab6:
        #st.write(' :rotating_light: Esse gráfico **não diz respeito à nenhuma métrica de bônus**, ele pontua a média de engajamento geral dos alunos ativos a fim de comparar com anos anteriores.:rotating_light:')

    hide_st_style="""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-9s5bis {visibility: visible;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
