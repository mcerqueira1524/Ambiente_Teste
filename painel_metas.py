
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from PIL import Image
from functools import reduce
import io
from io import BytesIO
from st_pages import Page, Section, add_page_title, show_pages
from streamlit_tags import st_tags


#favicon = Image.open("favicon.ico")

st.set_page_config(page_title = "Dash 360 IOL", layout="wide", initial_sidebar_state="collapsed")


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords_metas"]
            and st.session_state["password"]
            == st.secrets["passwords_metas"][st.session_state["username"]]
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
    ### login/senha sem tutores

    #@st.experimental_memo.clear()

    @st.experimental_memo
    def importar_dash360():
        df_dash360 = pd.read_excel(r"I:\PROJETOS\ISMART_ONLINE\0_Histórico_Alunos\Streamlit Dash\Bases_Github\Dash 360 Final_Tratado.xlsx")
        return df_dash360

    @st.experimental_memo
    def importar_historico_2021():
        df_2021 = pd.read_excel(r"I:\PROJETOS\ISMART_ONLINE\0_Histórico_Alunos\Streamlit Dash\Bases_Github\Historico_2021_Tratado.xlsx")
        return df_2021

    @st.experimental_memo
    def importar_historico_2020():
        df_2020 = pd.read_excel(r"I:\PROJETOS\ISMART_ONLINE\0_Histórico_Alunos\Streamlit Dash\Bases_Github\Historico_2020_Tratado.xlsx")
        return df_2020

    @st.experimental_memo
    def importar_historico_2022():
        df_2022 = pd.read_excel(r"I:\PROJETOS\ISMART_ONLINE\0_Histórico_Alunos\Streamlit Dash\Bases_Github\Historico_2022_Tratado.xlsx")
        return df_2022

    df_dash360 = importar_dash360()
    df_2021 = importar_historico_2021()
    df_2020 = importar_historico_2020()
    df_2022 = importar_historico_2022()

    #importando tabelas fato auxiliares
    @st.experimental_memo
    def importar_mos_merge(): # MOs
        df_mos_merge = pd.read_excel(r"I:\PROJETOS\ISMART_ONLINE\2022\Data Analytics\Streamlit Dash\Bases_Github\MOs Resumo_Tratado.xlsx")
        return df_mos_merge

    df_mos_merge = importar_mos_merge()

    #merge
    data_frames = [df_dash360, df_mos_merge]
    df_dash360 = reduce(lambda  left,right: pd.merge(left,right,on=['ID'],how='outer'), data_frames)

    #df de cálculo das metas
    df_selection = df_dash360[df_dash360['Status'] == "ATIVO"]
    #### filtros
    #gerando dois dataframes
    #um (principal) apenas com os alunos ativos
    #um com todos os alunos (a fim de verificar o aumento de desligados etc)

    #Título
    st.title('Painel de Metas')
    st.markdown("##")
    st.caption("Nesta aba, é possível verificar o atingimento das metas YTD (Year to date: do ano corrente até a última atualização)")
    ###Engajamento das atividades obrigatórias do ano

    #cáclulo da meta de 2023
    df_meta_acad = df_selection[df_selection['É liberado de Matemática ou Linguagens?'] == 'Não dispensado'] #para MA e LI contabilizamos apenas os não dispensados
    alto_engaj_ma = ((df_meta_acad[df_meta_acad['ALUNO ALTO ENGAJ MA?'] == 'SIM']['cont'].sum()/df_meta_acad['cont'].sum())*100)
    alto_engaj_li = ((df_meta_acad[df_meta_acad['ALUNO ALTO ENGAJ LI?'] == 'SIM']['cont'].sum()/df_meta_acad['cont'].sum())*100)
    alto_engaj_miss = ((df_selection[df_selection['ALUNO ALTO ENGAJ MISSÃO?'] == 'SIM']['cont'].sum()/df_selection['cont'].sum())*100)
    alto_engaj_red = ((df_selection[df_selection['ALUNO ALTO ENGAJ RED?'] == 'SIM']['cont'].sum()/df_selection['cont'].sum())*100)
    #alto_engaj_form  = ((df_selection[df_selection['Alto Engaj. Formações?'] == 'SIM']['cont'].sum()/df_selection['cont'].sum())*100)
    engaj = [alto_engaj_li,alto_engaj_ma,alto_engaj_red,alto_engaj_miss]
    ytd_engaj = round(np.mean(engaj),1)

    ytd_engaj = 60

    #ytd_forma = df_selection[df_selection['Média Formações']].mean() [[AJUSTAR]]
    ytd_forma = 50

    meta_70 = 0
    meta_80 = 50
    meta_90 = 80 #meta 100% é 90% de engaj acadêmico + formações
    meta_form = 67

    with st.expander('Engajamento'):
        st.markdown("<h2 style= 'text-align: center'> Engajamento </h2>", unsafe_allow_html=True)

        col1,col2,col3=st.columns([2,1,1])
        with col1:
            st.write('')
            st.write('Engajamento nas atividades obrigatórias do IOL (Matemática, Linguagens, Missão e Redação)')
            st.write('')
            st.write('')
            st.write('Média de presença nas formações')
        with col2:
            #YTD
            st.metric(label='YTD', value = ytd_engaj)
            st.metric(label='YTD', value = ytd_forma)
        with col3:
            #metas
            st.write('')
            #st.text('Metas sendo definidas')
            st.text(f'Metas:\n 70% = Acadêmico: {meta_70} \n 80% = Acadêmico: {meta_80} \n 90% = Acadêmico: {meta_90}\n 100% = Acadêmico: {meta_90} e Formações: {meta_form}')

        try:
            if ytd_engaj < meta_70:
                st.info('⚠️ Meta 70% ainda não atingida')
            elif ytd_engaj >= meta_90 & ytd_forma >= meta_form:
                st.info('😍 Meta 100% atingida em Engajamento e Formação')
            elif ytd_engaj >= meta_90 & ytd_forma >= meta_form:
                st.info('😀 Meta 90% atingida em Engajamento')
            elif ytd_engaj >= meta_80:
                st.info('🙂 Meta 80% atingida')
            elif ytd_engaj >= meta_70:
                st.info('😐 Meta 70% atingida')

        except ValueError:
            st.info('🤔 Meta ainda em andamento')


    #### MO's

    ytd_mo = 0 #[[AJUSTAR]]
    projecao_mo = 0 #[[AJUSTAR]]
    meta_70_mo = 10
    meta_80_mo = 0
    meta_90_mo = 0
    meta_100_mo = 0

    with st.expander('Melhores Oportunidades'):
        st.markdown("<h2 style= 'text-align: center'> Melhores Oportunidades </h2>", unsafe_allow_html=True)

        col1,col2,col3,col4=st.columns([2,1,1,1])
        with col1:
            st.write('')
            st.write('Aprovações em Melhores Oportunidades')
            st.write('')
        with col2:
            #YTD
            st.metric(label='YTD', value = ytd_mo)
        with col3:
            #Projeção
            st.metric(label='Projeção', value = projecao_mo)
        with col4:
            #metas
            st.write('')
            st.text(f'Metas:\n 70% = {meta_70_mo} \n 80% = {meta_80_mo} \n 90% = {meta_80_mo}\n 100% = {meta_100_mo}')


        try:
            if ytd_mo < meta_70_mo:
                st.info('⚠️ Meta 70% ainda não atingida')
            elif ytd_mo >= meta_100_mo:
                st.info('😍 Meta 100% atingida')
            elif ytd_mo >= meta_90_mo:
                st.info('😀 Meta 90% atingida')
            elif ytd_mo >= meta_80_mo:
                st.info('🙂 Meta 80% atingida')
            elif ytd_mo >= meta_70_mo:
                st.info('😐 Meta 70% atingida')

        except ValueError:
            st.info('🤔 Meta ainda em andamento')

    #### BT
    ytd_bt = 0 #[[AJUSTAR]]
    projecao_bt = 0 #[[AJUSTAR]]
    meta_70_bt = 10
    meta_80_bt = 0
    meta_90_bt = 0
    meta_100_bt = 0

    with st.expander('Bolsa Talento'):
        st.markdown("<h2 style= 'text-align: center'> Bolsa Talento </h2>", unsafe_allow_html=True)

        col1,col2,col3,col4=st.columns([2,1,1,1])
        with col1:
            st.write('')
            st.write('Aprovações em Bolsa Talento')
            st.write('')
        with col2:
            #YTD
            st.metric(label='YTD', value = ytd_bt)
        with col3:
            #Projeção
            st.metric(label='Projeção', value = projecao_bt)
        with col4:
            #metas
            st.write('')
            st.text(f'Metas:\n 70% = {meta_70_bt} \n 80% = {meta_80_bt} \n 90% = {meta_80_bt}\n 100% = {meta_100_bt}')

        try:
            if ytd_bt < meta_70_bt:
                st.info('⚠️ Meta 70% ainda não atingida')
            elif ytd_bt >= meta_100_bt:
                st.info('😍 Meta 100% atingida')
            elif ytd_bt >= meta_90_bt:
                st.info('😀 Meta 90% atingida')
            elif ytd_bt >= meta_80_bt:
                st.info('🙂 Meta 80% atingida')
            elif ytd_bt >= meta_70_bt:
                st.info('😐 Meta 70% atingida')

        except ValueError:
            st.info('🤔 Meta ainda em andamento')

    #### VESTIBULAR
    ytd_vest = 0 #[[AJUSTAR]]
    projecao_vest = 0 #[[AJUSTAR]]
    meta_70_vest = 10
    meta_80_vest = 0
    meta_90_vest = 0
    meta_100_vest = 0

    with st.expander('Vestibular'):
        st.markdown("<h2 style= 'text-align: center'> Vestibular </h2>", unsafe_allow_html=True)

        col1,col2,col3,col4=st.columns([2,1,1,1])
        with col1:
            st.write('')
            st.write('Aprovações em Cursos e Carreiras apoiadas')
            st.write('')
        with col2:
            #YTD
            st.metric(label='YTD', value = ytd_vest)
        with col3:
            #Projeção
            st.metric(label='Projeção', value = projecao_vest)
        with col4:
            #metas
            st.write('')
            st.text(f'Metas:\n 70% = {meta_70_vest} \n 80% = {meta_80_vest} \n 90% = {meta_80_vest}\n 100% = {meta_100_vest}')

        try:
            if ytd_vest < meta_70_vest:
                st.info('⚠️ Meta 70% ainda não atingida')
            elif ytd_vest >= meta_100_vest:
                st.info('😍 Meta 100% atingida')
            elif ytd_vest >= meta_90_vest:
                st.info('😀 Meta 90% atingida')
            elif ytd_vest >= meta_80_vest:
                st.info('🙂 Meta 80% atingida')
            elif ytd_vest >= meta_70_vest:
                st.info('😐 Meta 70% atingida')

        except ValueError:
            st.info('🤔 Meta ainda em andamento')


    hide_st_style="""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-9s5bis {visibility: visible;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
