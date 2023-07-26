
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from functools import reduce
import io
from io import BytesIO
from st_pages import Page, Section, add_page_title, show_pages
from streamlit_tags import st_tags


favicon = Image.open("favicon.ico")

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

    @st.cache_data.clear()

    @st.cache_data
    def importar_dash360():
        df_dash360 = pd.read_excel(r"Dash 360 Final_Tratado.xlsx")
        return df_dash360

    @st.cache_data
    def importar_historico_2021():
        df_2021 = pd.read_excel(r"Historico_2021_Tratado.xlsx")
        return df_2021

    @st.cache_data
    def importar_historico_2020():
        df_2020 = pd.read_excel(r"Historico_2020_Tratado.xlsx")
        return df_2020

    @st.cache_data
    def importar_historico_2022():
        df_2022 = pd.read_excel(r"Historico_2022_Tratado.xlsx")
        return df_2022

    df_dash360 = importar_dash360()
    df_2021 = importar_historico_2021()
    df_2020 = importar_historico_2020()
    df_2022 = importar_historico_2022()

    #importando tabelas fato auxiliares
    @st.cache_data
    def importar_olimp(): #olimpíadas
        df_olimp = pd.read_excel(r"Olimpiadas_Tratado.xlsx")
        return df_olimp

    @st.cache_data
    def importar_psico(): #Psicológico
        df_psico = pd.read_excel(r"Questões_Psicológicas_Tratado.xlsx")
        return df_psico

    @st.cache_data
    def importar_pu(): #PU
        df_pu = pd.read_excel(r"Provas Únicas_Tratado.xlsx")
        return df_pu

    @st.cache_data
    def importar_bt23(): #BT 23
        df_bt23 = pd.read_excel(r"Bolsa_Talento_2022.xlsx")
        return df_bt23
    df_olimp = importar_olimp()
    df_psico = importar_psico()
    df_pu = importar_pu()
    df_bt23 = importar_bt23()

    #merge com as tabelas fato
    olimp_merge = df_olimp.drop_duplicates(subset=['ID'])
    olimp_merge = olimp_merge.drop(columns = ['Mês','Data','Série','Nome', 'Olimpíada', 'Status da Inscrição','Status'])

    data_frames = [df_dash360, olimp_merge, df_psico, df_bt23]
    df_dash360 = reduce(lambda  left,right: pd.merge(left,right,on=['ID'],how='outer'), data_frames)

    #### filtros
    #gerando dois dataframes
    #um (principal) apenas com os alunos ativos
    #um com todos os alunos (a fim de verificar o aumento de desligados etc)

    #Título
    st.title('Download Base Filtrada')
    st.markdown("##")

    st.markdown("<h3 style= 'text-align: center'> Filtros </h3>", unsafe_allow_html=True)
    st.caption("Nesta aba, poderá fazer o download da base do IOL de acordo com os filtros que preferir! Abaixo estão os filtros padrão e em seguida pode selecionar qual coluna deseja baixar na seção 'Selecionar colunas da base baixada'. Na seção 'Filtrar a partir de lista de RAs', você pode inserir RA's específicos para recuperar a informação deles")

    col1,col2=st.columns(2)
    with col1:
        #filtro de status
        if 'ATIVO' in (df_dash360['Status'].tolist()):
            status = st.multiselect(
                "Selecione o status dos estudantes:",
                options=df_dash360['Status'].dropna().unique(),
                default='ATIVO',
                help = 'Por padrão, estão filtrados apenas os estudantes ATIVOS. Na lista, é possível selecionar os outros status.'
                )
        else:
            status = st.multiselect(
                "Selecione o status dos estudantes:",
                options=df_dash360['Status'].dropna().unique(),
                default=df_dash360['Status'].dropna().unique()
                )

        #filtro de tipo
        tipo = st.multiselect(
            "Selecione o tipo:",
            options=df_dash360['Tipo'].dropna().unique(),
            default=df_dash360['Tipo'].dropna().unique()
            )

        #tutor
        lista_tutores = df_dash360['Tutor'].dropna().unique().tolist()
        desfiltrartutor=st.checkbox("Desfiltrar Tutor",value=True)
        if desfiltrartutor:
            tutor=st.multiselect(
                "Selecione o tutor:",
                options=lista_tutores,
                default=lista_tutores
                )
        else:
            tutor = st.multiselect(
                "Selecione o tutor:",
                options=lista_tutores
                )
    with col2:
        #filtro de serie
        serie = st.multiselect(
            "Selecione a série:",
            options=df_dash360['Serie'].dropna().unique(),
            default=df_dash360['Serie'].dropna().unique()
            )

        #praça
        praca = st.multiselect(
            "Selecione a Praça:",
            options=df_dash360['Praça'].dropna().unique(),
            default=df_dash360['Praça'].dropna().unique()
            )
        #filtro de cluster [[AJUSTAR]] Visível apenas quando tiver engajamento
        #cluster = st.multiselect(
            #"Selecione a cluster:",
            #options=df_dash360['CLUSTER ENGAJAMENTO'].dropna().unique(),
            #default=df_dash360['CLUSTER ENGAJAMENTO'].dropna().unique()
            #)
        #[[AJUSTAR]] inserir filtro de engajamento: disciplina + operador (>/</>=/<=/==) + número


    #base com filtros que será usada nos gráficos
    df_selection = df_dash360.query("Status == @status & Serie == @serie & Tipo == @tipo & Praça == @praca & Tutor == @tutor")

    with st.expander('Selecionar colunas da base para baixar'):

        lista_colunas = df_dash360.columns.tolist()

        #formatos de colunas pré-selecionadas
        formatos = st.radio("Colunas pré-selecionadas para download da base:",("Formato Relatório de Engajamento (ID, Nome, Série, E-mail, E-mail do Responsável, Cluster de Engajamento, Média de Engajamento em Matemática, Linguagens, Missões e Redação)",
                                                               "Formato Bibot",
                                                               "Todas as colunas"))

        #colunas_relatorio = st.checkbox("Formato Relatório de Engajamento",value=True) #default
        lista_relatorio =['ID',
                        'Nome',
                        'Serie',
                        'E-mail Estudante',
                        'RESPONSÁVEL 1 - E-mail',
                        'MÉDIA ENGAJAMENTO MA',
                        'MÉDIA ENGAJAMENTO LI',
                        'MÉDIA ENGAJAMENTO MISSÕES',
                        'MÉDIA ENGAJAMENTO REDAÇÃO',
                        'MÉDIA ENGAJAMENTO',
                        'CLUSTER ENGAJAMENTO']

        #colunas_bibot = st.checkbox("Formato Bibot")
        lista_bibot =['ID',
                        'Nome',
                        'Serie',
                        'Praça Aluno', #contém Sorocaba e Cotia. A variável "Praça" é [SJC,SP,BH,RJ], em que SP = são paulo, sorocaba e cotia
                        'Tutor',
                        'E-mail Estudante',
                        'RESPONSÁVEL 1 - E-mail',
                        'MÉDIA ENGAJAMENTO MA',
                        'MÉDIA ENGAJAMENTO LI',
                        'MÉDIA ENGAJAMENTO MISSÕES',
                        'MÉDIA ENGAJAMENTO REDAÇÃO',
                        'MÉDIA ENGAJAMENTO',
                        'CLUSTER ENGAJAMENTO']

        #colunas_todas = st.checkbox("Todas as colunas")

        if formatos == "Formato Relatório de Engajamento (ID, Nome, Série, E-mail, E-mail do Responsável, Cluster de Engajamento, Média de Engajamento em Matemática, Linguagens, Missões e Redação)":
            cols = st.multiselect(
                    "Colunas disponíveis para download:",
                    options = lista_colunas,
                    default = lista_relatorio
                    )
            #colocar aqui a lógica de texto do relatório de engajamento no futuro
        elif formatos == "Formato Bibot":
            cols = st.multiselect(
                    "Colunas disponíveis para download:",
                    options = lista_colunas,
                    default = lista_bibot
                    )
        elif formatos == "Todas as colunas":
            cols = st.multiselect(
                "Colunas disponíveis para download:",
                options = lista_colunas,
                default = lista_colunas
                )
        else:
            cols = st.multiselect(
                "Colunas disponíveis para download:",
                options = lista_colunas,
                default = lista_colunas
                )

        df_selection = df_selection[cols]


    with st.expander('Filtrar a partir de lista de RAs'):
        ras_filtro_lista = st_tags(
            label="RA's a serem filtrados:",
            text="Pressione Enter para adicionar novos RA's (apenas números)",
            maxtags=500,
            key=None)

        if len(ras_filtro_lista) > 0:
            try:
                #tem de transformar a lista que tá em str para float, porque o df_selection['ID'] é float
                #caso o RA não seja números, vai dar erro aqui
                ras_filtro = pd.DataFrame(columns = ['ID'],data = map(float, ras_filtro_lista))
                #merge o df inserido pelo usuário e aquele no dash 360
                frames = [ras_filtro,df_selection]
                df_selection = reduce(lambda  left,right: pd.merge(left,right,on=['ID'],how='inner'), frames)
                st.write(f"RA's digitados: {ras_filtro_lista}")
                st.write(f"Quantidade de RA's digitados: {len(ras_filtro_lista)}")
                st.write(f"Quantidade de RA's encontrados: {len(df_selection['ID'])}")
            except ValueError:
                st.warning('⚠️ Digite apenas números')

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
        processed_data = output.getvalue()
        return processed_data
    df_xlsx = to_excel(df_selection)
    st.download_button(label='📥 Download Base Filtrada',
                            data=df_xlsx,
                            file_name= 'Base de dados 360 IOL.xlsx')
    if df_selection.empty:
        st.warning('⚠️ RA(s) não encontrados')
    df_selection
    #colocar mensagem de erro
    hide_st_style="""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-9s5bis {visibility: visible;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
