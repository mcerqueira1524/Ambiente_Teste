import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from functools import reduce
import io
from io import BytesIO
from st_pages import Page, Section, add_page_title, show_pages

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
    #limpar o cache e atualizar as planilhas
    #@st.cache_data.clear()
    
    #importando o Dash 360
    @st.cache_data
    def importar_dash360():
        df_dash360 = pd.read_excel(r"Dash 360 Final_Tratado.xlsx")
        return df_dash360

    df_dash360 = importar_dash360()
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
    def importar_psico():
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

    #__________________ #Copiar aqui ___________

    df_olimp = importar_olimp()
    df_psico = importar_psico()
    df_pu = importar_pu()
    df_bt23 = importar_bt23()

    #merge com as tabelas fato
    olimp_merge = df_olimp.drop_duplicates(subset=['ID'])
    olimp_merge = olimp_merge.drop(columns = ['Mês','Data','Série','Nome', 'Olimpíada', 'Status da Inscrição','Status'])

    data_frames = [df_dash360, olimp_merge, df_psico, df_bt23]
    df_dash360 = reduce(lambda  left,right: pd.merge(left,right,on=['ID'],how='outer'), data_frames)

    #Título
    st.title('Dashboard Micro')
    st.markdown("##")

    #----------primeira linha-------

    desfiltrartutor=st.button("Desfiltrar Tutor")
    if desfiltrartutor:
        tutor=st.multiselect(
            "Selecione o tutor para filtrar o nome do estudante:",
            options=df_dash360['Tutor'].dropna().unique()

            )
    else:
        tutor = st.multiselect(
            "Selecione o tutor:",
            options=df_dash360['Tutor'].dropna().unique(),
            default=df_dash360['Tutor'].dropna().unique()
            )
    #fitlrando dash por Tutor
    df_selection = df_dash360.query('Tutor == @tutor')

    col1, col2, col3 = st.columns(3,gap='large')
    with col2:
        #Nomes da seleção do dash micro: ordenando por ordem alfabética e depois deixando apenas os valores únicos
        nomes = df_selection[['Nome']].sort_values(by=['Nome'])
        nomes = nomes['Nome'].unique()
        nomes = nomes[~pd.isnull(nomes)]

        #lista suspensa para selecionar
        nome = st.selectbox('Selecione o nome do/a estudante:', options= nomes) #opção de selecionar estudante
        df_selection = df_selection.query("Nome == @nome") #filtrar o nome do estudante no dash
        id = df_selection['ID'].values[0] #a partir do nome, buscar RA/ID Ismart do estudante pelo Dash

        #usando ID/RA para buscar as notas da PU e histórico de ENGAJAMENTO
        df_selection_pu = df_pu[df_pu['ID'] == id]
        df_selection_2022 = df_2022_yoy[df_2022_yoy['ID'] == id]
        df_selection_2021 = df_2021_yoy[df_2021_yoy['ID'] == id]
        df_selection_2020 = df_2020_yoy[df_2020_yoy['ID'] == id]

    #nome do aluno selecionado logo abaixo
    nome_titulo = f"""<h1 style = "text-align: center;"><span style="word-wrap:break-word;">
                    {nome}
                </span> </h1>"""
    st.markdown(nome_titulo, unsafe_allow_html=True)

    ### ----- gerar variáveis

    #em muitas das bases só não tem certas informações, no excel isso seria uma célula em branco
    #no pandas, é interpretado como nan. Ademais, sempre passo as variáveis como string então fica 'nan'
    #assim, a função abaixo é para passar as variáveis sempre que estiver vazio retornar '-'
    def nulo_vazio(var):
        if var == "nan":
            return "-"
        else:
            return var

    ## todas as variável tem de ser filtradas pelo nome da coluna, transformada em str e depois passar pelo nulo_vazio
    ## essa função ajuda a ser mais fácil
    ## inseri essa função em jan/23 depois de boa parte do dash já estar pronto, portanto, nem sempre a utilizo
    def trat_coluna(nome_coluna):
        variavel = str(df_selection[nome_coluna].values[0])
        variavel = nulo_vazio(variavel)
        return variavel
    #####identificadores Ismart
    ra = str(df_selection['ID'].values[0])
    id_eduquo = str(df_selection['ID Eduquo/SAS'].values[0])
    status = str(df_selection['Status'].values[0])

    if status == "DESLIGADO":
        data_desligamento = trat_coluna('DESLIGAMENTO - Data do Desligamento')
        motivo_desligamento = trat_coluna('DESLIGAMENTO - Motivo do Desligamento')
    elif status == "AFASTADO":
        data_afastamento = trat_coluna('AFASTAMENTO - Data do Afastamento')
        data_retorno = trat_coluna('AFASTAMENTO - Data do Retorno')

    serie = trat_coluna('Serie')
    praca = trat_coluna('Praça Aluno')
    tipo = trat_coluna('Tipo')
    tutor = trat_coluna('Tutor')
    cluster = trat_coluna('CLUSTER ENGAJAMENTO')
    dispensa = trat_coluna('É liberado de Matemática ou Linguagens?')
    ano_entrada = df_selection['Ano de entrada do(a) estudante '].values[0].astype(int)

    ######dados de pessoais
    data_nascimento = trat_coluna('Data de nascimento')
    sexo = trat_coluna('Sexo ')
    raca = trat_coluna('Raça/Cor')
    renda = trat_coluna('Renda per capita')
    id_genero = trat_coluna('Identidade de gênero')
    escola_nome = trat_coluna('ESCOLA - Nome da escola')
    escola_classificacao = trat_coluna('ESCOLA - Classificação')
    escola_periodo = trat_coluna('ESCOLA - Período')


    ####dados de contato
    email = trat_coluna('E-mail Estudante')
    telefone = trat_coluna('Telefone')
    telefone_pessoal = trat_coluna('TELEFONE - Telefone pessoal do aluno?')

    #responsável1
    resp1_nome = trat_coluna('RESPONSÁVEL 1 - Nome')
    resp1_email = trat_coluna('RESPONSÁVEL 1 - E-mail')
    resp1_telefone = trat_coluna('RESPONSÁVEL 1 - Telefone')

    #responsável2
    resp2_nome = trat_coluna('RESPONSÁVEL 2 - Nome')

    resp2_email = trat_coluna('RESPONSÁVEL 2 - E-mail')
    resp2_telefone = trat_coluna('RESPONSÁVEL 2 - Telefone')
 
    ###__________LAYOUT_________

    ### informações iniciais
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7,gap='small')
    with col1:
        st.text(f'RA: {ra}')
    with col2:
        st.text(f'Status: {status}')
    with col3:
        st.text(f'{serie}')
    with col4:
        st.text(f'Tipo: {tipo}')
    with col5:
        st.text(f'{praca}')
    with col6:
        st.text(f'Tutor(a): {tutor}')
    with col7:
        st.text(f'{dispensa}')

    st.write('')
    st.markdown("""<h3 style = "text-align: center"> <b> Informações Gerais </b> </h3>""", unsafe_allow_html=True)
    st.markdown('---')

    #informações gerais
    col1,col2 = st.columns(2,gap='small')

    with col1:
        with st.expander('Dados do estudante'):
            st.subheader('Dados do estudante')
            st.write(f'**Data de Nascimento:** {data_nascimento}')
            st.write(f'**Gênero/Sexo:** {sexo} {id_genero}')
            st.write(f'**Raça/Cor:** {raca}')
            st.write(f'**Escola:** {escola_nome}')
            st.write(f'**Classificação Escola:** {escola_classificacao}')
            st.write(f'**Período Escolar:** {escola_periodo}')
            st.write(f'**Ano de entrada no Ismart:** {ano_entrada}')
            st.write(f'**Renda:** {renda}')
    with col2:
        with st.expander('Dados de contato'):
            st.subheader('Estudante')
            st.write(f'**E-mail:** {email}')
            st.write(f'**Telefone:** {telefone} **- Celular de uso pessoal do aluno?** {telefone_pessoal}')
            st.subheader('Responsável 1')
            st.write(f'**Nome:** {resp1_nome}')
            st.write(f'**E-mail:** {resp1_email}')
            st.write(f'**Telefone:** {resp1_telefone}')
            st.subheader('Responsável 2')
            st.write(f'**Nome:** {resp2_nome}')
            st.write(f'**E-mail:** {resp2_email}')
            st.write(f'**Telefone:** {resp2_telefone}')

    #engajamento atualizado
    if dispensa == 'Dispensado':
        ma = "Dispensado"
        li = 'Dispensado'
    else:
        ma = int(df_selection['MÉDIA ENGAJAMENTO MA'].values[0])
        li = int(df_selection['MÉDIA ENGAJAMENTO LI'].values[0])

    miss = int(df_selection['MÉDIA ENGAJAMENTO MISSÕES'].values[0])
    red = int(df_selection['MÉDIA ENGAJAMENTO REDAÇÃO'].values[0])
    engaj = int(df_selection['MÉDIA ENGAJAMENTO'].values[0])


    ##Gráficos
    template_dash = "plotly_white"
    bg_color_dash = "rgba(0,0,0,0)"
    #cores nessa ordem: Rosa choque; Amarelo; Azul escuro; verdinho; azul normal; salmão; verdinho escuro; Azul clarinho; laranja claro;
    colors = ['#EE2D67','#EBEA70','#002561','#8EC6B2','#008ED4','#F2665E', '#55AA8C','#C4ECFF','#FCBD7D']

    ###MISSÕES FEITAS
    colunas_mods_miss = ['MISSÃO 1',
                        'MISSÃO 2',
                        'MISSÃO 3',
                        'MISSÃO 4',
                        'MISSÃO 5',
                        'MISSÃO 6',
                        'MISSÃO 7']

    mods_miss = df_selection[colunas_mods_miss].transpose().reset_index()
    mods_miss['% engajamento'] = round(mods_miss.iloc[:, 1])

    fig_mods_miss = px.bar(
        mods_miss,
        x='index',
        y='% engajamento',
        text = "% engajamento",
        color = 'index',
        color_discrete_sequence = ['#008ED4'],
        template = template_dash,
        orientation='v')

    fig_mods_miss.update_layout(
        showlegend=False,
        yaxis_title="% de Engajamento",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> MISSÃO: % ENGAJAMENTO EM CADA MÓDULO </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    fig_mods_miss.update_traces(texttemplate='%{y}%', textposition='inside')

    fig_mods_miss.update_yaxes(visible=False, showticklabels=False)

    fig_mods_miss.update_xaxes(title="")

    ###REDAÇÕES FEITAS
    #identificando quais redações o estudante fez
    def engaj_red(redacao):
        list = []
        for row in df_selection[redacao]:
            if row == '-':
                realizacao = 0
                list.append(realizacao)
            elif row == 'nan':
                realizacao = 0
                list.append(realizacao)
            else:
                realizacao = 100
                list.append(realizacao)
        return list

    df_selection['DIAGNÓSTICA ESCRITA_Realização'] = engaj_red('DIAGNÓSTICA ESCRITA')
    df_selection['DIAGNÓSTICA REESCRITA_Realização'] = engaj_red('DIAGNÓSTICA REESCRITA')
    df_selection['RED 1 ESCRITA_Realização'] = engaj_red('RED 1 ESCRITA')
    df_selection['RED 1 REESCRITA_Realização'] = engaj_red('RED 1 REESCRITA')
    df_selection['RED 2 ESCRITA_Realização'] = engaj_red('RED 2 ESCRITA')
    df_selection['RED 2 REESCRITA_Realização'] = engaj_red('RED 2 REESCRITA')
    df_selection['RED 3 ESCRITA_Realização'] = engaj_red('RED 3 ESCRITA')
    df_selection['RED 3 REESCRITA_Realização'] = engaj_red('RED 3 REESCRITA')
    df_selection['RED 4 ESCRITA_Realização'] = engaj_red('RED 4 ESCRITA')
    df_selection['RED 4 REESCRITA_Realização'] = engaj_red('RED 4 REESCRITA')
    df_selection['RED 5 ESCRITA_Realização'] = engaj_red('RED 5 ESCRITA')
    df_selection['RED 5 REESCRITA_Realização'] = engaj_red('RED 5 REESCRITA')
    df_selection['RED 6 ESCRITA_Realização'] = engaj_red('RED 6 ESCRITA')
    df_selection['RED 6 REESCRITA_Realização'] = engaj_red('RED 6 REESCRITA')

    colunas_mods_red = ['DIAGNÓSTICA ESCRITA_Realização',
                        'DIAGNÓSTICA REESCRITA_Realização',
                        'RED 1 ESCRITA_Realização',
                        'RED 1 REESCRITA_Realização',
                        'RED 2 ESCRITA_Realização',
                        'RED 2 REESCRITA_Realização',
                        'RED 3 ESCRITA_Realização',
                        'RED 3 REESCRITA_Realização',
                        'RED 4 ESCRITA_Realização',
                        'RED 4 REESCRITA_Realização',
                        'RED 5 ESCRITA_Realização',
                        'RED 5 REESCRITA_Realização',
                        'RED 6 ESCRITA_Realização',
                        'RED 6 REESCRITA_Realização']

    mods_red = df_selection[colunas_mods_red].transpose().reset_index()
    mods_red['nota'] = mods_red.iloc[:, 1]

    fig_mods_red = px.bar(
        mods_red,
        x='index',
        y='nota',
        text = "nota",
        color = 'index',
        color_discrete_sequence = ['#8EC6B2'],
        template = template_dash,
        orientation='v')

    fig_mods_red.update_layout(
        showlegend=False,
        yaxis_title="Nota Final",
        plot_bgcolor=bg_color_dash,
        title={
            'text': "<b> REDAÇÃO: ENGAJAMENTO EM CADA REDAÇÃO </b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    fig_mods_red.update_traces(textposition='inside')

    fig_mods_red.update_yaxes(visible=False, showticklabels=False)

    fig_mods_red.update_xaxes(title="")

    ## tabela com os motivos de zero
    cols_motivo_zero = ["REDAÇÃO - DIAGNÓSTICA ESCRITA - Motivo de zero ",
                        "REDAÇÃO - DIAGNÓSTICA REESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 1 ESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 1 REESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 2   ESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 2  REESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 3   ESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 3   REESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 4   ESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 4   REESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 5   ESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 5   REESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 6   ESCRITA - Motivo de zero",
                        "REDAÇÃO - RED 6   REESCRITA - Motivo de zero"]
    ## interação da lista de colunas tratando cada coluna de motivo de zero
    for i in cols_motivo_zero:
            df_selection[i] = trat_coluna(i)

    #transpondo e selecionando as colunas da tabela de motivos de zero
    df_show_motivos_zero = df_selection[cols_motivo_zero].transpose().reset_index()
    df_show_motivos_zero.rename(columns = {df_show_motivos_zero.columns[0]: "Temas da Redação", df_show_motivos_zero.columns[1]: "Motivos de Zero"},inplace = True)
    #engajamento geral
    st.markdown("<h2 style= 'text-align: center'> Engajamento 2023 </h2>", unsafe_allow_html=True)
    st.caption("O engajamento sempre é atualizado na segunda-feira, tendo como referência o realizado pelo aluno até o último domingo. Para conferir a última data de atualização desse Dash, confira na aba Leia-me em 'Atualizações Fixas'.")

    #métricas de engajamento
    espaco1,col1,col2,espaco2 = st.columns([1,1,1,1])
    with col1:
        st.metric('Média de Matemática',value = ma)
        st.metric('Média de Linguagens',value = li)
    with col2:
        st.metric('Média de Missão',value = miss)
        st.metric('Média de Redação',value = red)

    espaco1,col3,espaco2 = st.columns([1,2,1])
    with col3:
        st.metric('Média Geral',value = engaj)
        st.metric(f'Cluster de Engajamento', value = cluster)


    if (dispensa == "Não dispensado") & ((serie == '1º EM') | (serie == '2º EM')):
         ##Engajamento nos módulos de linguagens
        colunas_mods_li = [ 'LI - MODULO 1',
                            'LI - MODULO 2',
                            'LI - MODULO 3',
                            'LI - MODULO 4',
                            'LI - MODULO 5',
                            'LI - MODULO 6',
                            'LI - MODULO 7',
                            'LI - MODULO 8',
                            'LI - MODULO 9',
                            'LI - MODULO 10',
                            'LI - MODULO 11',
                            'LI - MODULO 12',
                            'LI - MODULO 13',
                            'LI - MODULO 14',
                            'LI - MODULO 15',
                            'LI - MODULO 16',
                            'LI - MODULO 17',
                            'LI - MODULO 18',
                            'LI - MODULO 19',
                            'LI - MODULO 20',
                            'LI - MODULO 21',
                            'LI - MODULO 22',
                            'LI - MODULO 23',
                            'LI - MODULO 24',
                            'LI - MODULO 25',
                            'LI - MODULO 26',
                            'LI - MODULO 27',
                            'LI - MODULO 28',
                            'LI - MODULO 29',
                            'LI - MODULO 30'
                            ]

        mods_li = df_selection[colunas_mods_li].transpose().reset_index()
        mods_li['% engajamento'] = round(mods_li.iloc[:, 1])

        fig_mods_li = px.bar(
            mods_li,
            x='index',
            y='% engajamento',
            text = "% engajamento",
            color = 'index',
            color_discrete_sequence = ['#EBEA70'],
            template = template_dash,
            orientation='v',
            )

        fig_mods_li.update_layout(
            showlegend=False,
            yaxis_title="% de Engajamento",
            plot_bgcolor=bg_color_dash,
            title={
                'text': "<b> LINGUAGENS: % ENGAJAMENTO EM CADA MÓDULO </b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        fig_mods_li.update_traces(texttemplate='%{y}%', textposition='inside', textangle=90)

        fig_mods_li.update_yaxes(visible=False, showticklabels=False)

        fig_mods_li.update_xaxes(tickangle=90,title="")

        st.plotly_chart(fig_mods_li,use_container_width=True)

    #engajamento em miss e redação
    st.plotly_chart(fig_mods_miss,use_container_width=True)

    st.plotly_chart(fig_mods_red,use_container_width=True)

    #tabela com os motivos de zero
    espaco1,col1,espaco1 = st.columns([1,4,1])
    with col1:
        st.table(data = df_show_motivos_zero)

    #gerar gráficos de 'Prova Única' e 'Formação' fora das tabs
    #arrumar a base de PU primeiro

    ##tabs: inglês online, trilha tech (incluir hackathon) e MO's (se for do 9ºEF)
    tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs(['Prova Única','Histórico Engajamento','Formações','Psicológico','Flags/Sinalizações','Destaques','Outros'])
    with tab1:
        st.markdown("<h2 style= 'text-align: center'> Prova Única </h2>", unsafe_allow_html=True)
        if df_selection_pu.empty:
            st.write(":confused: Não foram encontradas notas de PU desse estudante")
        else:
            col1,espaco1 = st.columns([1,2])
            with col1:
                if ((serie == '8º EF') | (serie == '9º EF')):
                    cadernos_pu =['Média Geral','MA','LI']
                else:
                    cadernos_pu =['Média Geral','MA','LI','CN', 'CH']

                caderno = st.selectbox('Selecione o caderno', cadernos_pu)
            col11,col12 = st.columns([1,1])
            with col11:
                df_caderno_pu = df_selection_pu[df_selection_pu['Área'] == caderno].round()

                #gráfico com enem projetada
                df_graf_caderno_pu = df_caderno_pu[['PU','Área','ENEM_Projetado']]
                df_graf_caderno_pu['ENEM_Projetado'] = df_graf_caderno_pu['ENEM_Projetado'].astype(int)

                fig_graf_caderno_pu = px.bar(
                    df_graf_caderno_pu,
                    x="PU",
                    y='ENEM_Projetado',
                    text = 'ENEM_Projetado',
                    color = "PU",
                    template = template_dash,
                    color_discrete_sequence=colors
                )

                fig_graf_caderno_pu.update_layout(
                    showlegend=False,
                    xaxis_title="Prova Única",
                    yaxis_title="Nota Enem Projetado",
                    plot_bgcolor=bg_color_dash,
                    title={
                        'text': "<b> NOTA PU ENEM PROJETADO: "+caderno+"</b>",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )

                st.plotly_chart(fig_graf_caderno_pu,use_container_width=True)
            with col12:
                #apresentar esse dataframe
                df_show_caderno_pu = df_caderno_pu[['NOME', 'PU', 'Desempenho', 'Média_ENEM','ENEM_Projetado', 'Área']]
                df_show_caderno_pu['Desempenho'] = df_show_caderno_pu['Desempenho'].astype(int)
                df_show_caderno_pu['Média_ENEM'] = df_show_caderno_pu['Média_ENEM'].astype(int)
                df_show_caderno_pu['ENEM_Projetado'] = df_show_caderno_pu['ENEM_Projetado'].astype(int)
                st.dataframe(df_show_caderno_pu)
    with tab2:
        st.markdown("<h2 style= 'text-align: center'> Histórico de Engajamento </h2>", unsafe_allow_html=True)
        if (df_selection_2022.empty | ano_entrada == 2023):
            st.write(":confused: Não foi encontrado Histórico de Engajamento desse estudante")
        else:
            col1,espaco1 = st.columns([1,2])
            with col1:
                #dependendo do ano de entrada define quantas opções de histórico
                ## [[AJUSTAR]] - QUando tiver 2023 no engajamento mensal, colocar aqui tbm
                if ano_entrada == 2023:
                    anos_hist = [2023]
                elif ano_entrada == 2022:
                    anos_hist = [2022]
                elif ano_entrada == 2021:
                    anos_hist = [2022,2021]
                elif ano_entrada <= 2021:
                    anos_hist = [2022,2021,2020]

                #drop select de qual ano quer o histórico
                ano_engaj = st.selectbox('Selecione o ano de histórico', anos_hist)

            colunas_ano = ['Mês','MA','LI','MISS','RED','MÉDIA ENGAJAMENTO']

            if ano_engaj == 2021:
                df_ano = df_selection_2021
                df_ano['MA'] = df_ano['MA']
                df_ano['LI'] = df_ano['LI']
                df_ano['MISS'] = df_ano['MISS']
                df_ano['RED'] = df_ano['RED']
                df_ano['MÉDIA ENGAJAMENTO'] = df_ano['MÉDIA ENGAJAMENTO']
            elif ano_engaj == 2020:
                df_ano = df_selection_2020
                df_ano['MA'] = df_ano['MA']
                df_ano['LI'] = df_ano['LI']
                df_ano['MISS'] = df_ano['MISS']
                df_ano['RED'] = df_ano['RED']
                df_ano['MÉDIA ENGAJAMENTO'] = df_ano['MÉDIA ENGAJAMENTO']
            elif ano_engaj == 2022:
                df_ano = df_selection_2022

            ano_engaj = str(ano_engaj)#string para colocar no nome do gráfico
            #transformando o df para ser usado no gráfico
            engaj_hist = df_ano[colunas_ano]
            engaj_hist = pd.melt(engaj_hist,id_vars=['Mês'],value_vars=['MA','LI','MISS','RED','MÉDIA ENGAJAMENTO'], var_name='Disciplina', value_name='Engajamento')
            engaj_hist['Engajamento'] = engaj_hist['Engajamento'].round()#.astype(int)

            fig_engaj_hist = px.bar(
                engaj_hist,
                x="Mês",
                y="Engajamento",
                text = "Engajamento",
                color = 'Disciplina',
                category_orders={'Mês':['Abril','Maio','Junho','Julho','Agosto', 'Setembro', 'Outubro', 'Novembro','Dezembro']},
                template = template_dash,
                color_discrete_map= {'MA':'#EE2D67','LI':'#EBEA70','MISS':'#002561', 'RED':'#8EC6B2', 'MÉDIA ENGAJAMENTO':'#008ED4'},
                barmode='group'
            )

            fig_engaj_hist.update_layout(
                showlegend=True,
                xaxis_title="Mês",
                yaxis_title="% Porcentagem",
                plot_bgcolor=bg_color_dash,
                title={
                    'text': "<b> ENGAJAMENTO MÊS A MÊS: "+ano_engaj+"</b>",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )

            fig_engaj_hist.update_yaxes(visible=False)

            st.plotly_chart(fig_engaj_hist,use_container_width=True)
    with tab3:
        st.markdown("<h2 style= 'text-align: center'> Presenças e Justificativas nas Formações 2022</h2>", unsafe_allow_html=True)

        f1_presenca = trat_coluna('Presença 1ªF')
        f1_justificativa = trat_coluna('Justificativa 1ªF')

        f2_presenca = trat_coluna('Presença 2ªF')
        f2_justificativa = trat_coluna('Justificativa 2ªF')

        f3_presenca = trat_coluna('Presença 3ªF')
        f3_justificativa = trat_coluna('Justificativa 3ª F')

        f4_presenca = trat_coluna('Presença 4ªF')
        f4_justificativa = trat_coluna('Justificativa 4ªF')

        def emoji_presenca(var):
            if var == '100':
                emoji = 'Sim :white_check_mark:'
            elif var == '0':
                emoji = 'Não :x:'
            else:
                emoji = 'Ainda não foi registrada presença nessa formação :heavy_minus_sign:'
            return emoji

        col1,col2 = st.columns(2,gap='small')
        with col1:
            st.write(f'**Presente na 1ª formação:** {emoji_presenca(f1_presenca)}')
            st.write(f'**Presente na 2ª formação:** {emoji_presenca(f2_presenca)}')
            st.write(f'**Presente na 3ª formação:** {emoji_presenca(f3_presenca)}')
            st.write(f'**Presente na 4ª formação:** {emoji_presenca(f4_presenca)}')

        with col2:
            if f1_presenca == '0':
                st.write(f'**Justificativa 1ª formação:** {f1_justificativa}')
            if f2_presenca == '0':
                st.write(f'**Justificativa 2ª formação:** {f2_justificativa}')
            if f3_presenca == '0':
                st.write(f'**Justificativa 3ª formação:** {f3_justificativa}')
            if f4_presenca == '0':
                st.write(f'**Justificativa 4ª formação:** {f4_justificativa}')

    with tab4:
        st.markdown("<h2 style= 'text-align: center'> Questões Psicológicas </h2>", unsafe_allow_html=True)

        psico_quando = str(df_selection['Quando'].values[0])

        if psico_quando == "nan":
            st.write('**Identificadas questões psicológicas:** Não')
        else:
            st.write('**Identificadas questões psicológicas:** Sim')
            psico_caso_status = trat_coluna('STATUS')
            psico_ideacao = trat_coluna('Tem ideação?')
            psico_tentativa = trat_coluna('Teve tentativa?')
            psico_atendimento_psico = trat_coluna('Atendimento Psicológico?')
            psico_atendimento_psiqu = trat_coluna('Atendimento Psiquiátrico?')

            if len(psico_quando) > 10: #Alguns estão como '2022', outros com identif
                psico_quando = psico_quando[0:10]
                st.write(f'**Quando foi detectada a situação?** {psico_quando}')
            else:
                st.write(f'**Quando foi detectada a situação?** {psico_quando}')

            st.write(f'**Status:** {psico_caso_status}')
            st.write(f'**Atendimento Psicológico?** {psico_atendimento_psico}')
            st.write(f'**Atendimento Psiquiátrico?** {psico_atendimento_psiqu}')
            st.write(f'**Ideação Suicida:** {psico_ideacao}')
            st.write(f'**Tentativa Suicida:** {psico_tentativa}')

    with tab5:

        tweet = trat_coluna('2022 HISTÓRICO ALUNO - Tweet')
        if tweet == '-' or tweet == '0':
            st.write('')
        else:
            st.markdown("<h2 style= 'text-align: center'> Resumo do Aluno 2022 </h2>", unsafe_allow_html=True)
            st.write(f'{tweet}')


        psel23_8ef = trat_coluna('8º EF 2023 - Processo Seletivo')

        if psel23_8ef != '-':
            st.markdown("<h2 style= 'text-align: center'> Flags e Sinalizações </h2>", unsafe_allow_html=True)
            st.write(f'**Flag - Processo Seletivo 2023:** {psel23_8ef}')

        ressalva_0822 = trat_coluna('ANO 2022 - DESLIGAMENTO AGOSTO - Alunos não desligados')
        ressalva_1122 = trat_coluna('ANO 2022 - DESLIGAMENTO NOVEMBRO - Alunos não desligados')
        ressalva_0123 = trat_coluna('ANO 2023 - DESLIGAMENTO JANEIRO - Alunos não desligados')
        ressalva_0523 = trat_coluna('ANO 2023 - DESLIGAMENTO JUNHO - Alunos não desligados')

        if ressalva_0822 == "-" and ressalva_1122 == '-'and ressalva_0123 == '-'and ressalva_0523 == '-':
            st.write('')
        else:
            st.markdown("<h2 style= 'text-align: center'> Ressalvas Desligamentos </h2>", unsafe_allow_html=True)
            if ressalva_0822 != '-':
                st.write(f'**2022 - Desligamento Agosto:** {ressalva_0822}')
            if ressalva_1122 != '-':
                st.write(f'**2022 - Desligamento Novembro:** {ressalva_0822}')
            if ressalva_0123 != '-':
                st.write(f'**2023 - Desligamento Janeiro:** {ressalva_0123}')
            if ressalva_0123 != '-':
                st.write(f'**2023 - Desligamento Maio:** {ressalva_0523}')
    
    with tab6:
        st.markdown("<h2 style= 'text-align: center'> Atividades Extracurriculares </h2>", unsafe_allow_html=True)
        st.write ('Todas as informações abaixo foram obtidas da atualização cadastral de março de 2023')  

        col1, col2 = st.columns(2,gap='small')
        with col1:
            st.markdown("<h2 style= 'text-align: center'> Destaques Acadêmicos </h2>", unsafe_allow_html=True)

            #variáveis
            destaques = trat_coluna('DESTAQUES ACADÊMICOS - Olimpíadas, simulados, ranking da escola, feiras de ciências')
            trab_social = trat_coluna('OUTROS - Trabalho social')
            trab_social_detalhe = trat_coluna('OUTROS - Trabalho social - Detalhamento')
            extracurricular_passado = trat_coluna('OUTROS - Atividades Extracurriculares já realizadas no passado')
            extracurricular_hj = trat_coluna('OUTROS - Atividades Extracurriculares realizadas hoje')
            extracurricular_horas = trat_coluna('OUTROS - Quantidade de horas dedicadas a outras atividades extracurriculares')

            #print na tela
            st.write(f'**Quais atividades extracurriculares realiza atualmente?** {extracurricular_hj}')
            st.write(f'**Quais atividades extracurriculares já realizou no passado?** {extracurricular_passado}')
            st.write(f'**Quantidade de horas dedicadas a outras atividades extracurriculares?** {extracurricular_horas}')
            st.write(f'**Possui destaques acadêmicos?** {destaques}')
            st.write(f'**Já realizou trabalhos sociais?** {trab_social}')

            if trab_social != 'nan':
                st.write(f'**Já realizou trabalhos sociais?:** {trab_social_detalhe}')
                       
        with col2:
            st.markdown("<h2 style= 'text-align: center'> Inglês </h2>", unsafe_allow_html=True)
            
            #variáveis
            idioma_curso = trat_coluna('IDIOMAS - Curso de Inglês')
            idioma_entend = trat_coluna('IDIOMAS - Conhecimento de Inglês: Entendimento')
            idioma_leitura = trat_coluna('IDIOMAS - Conhecimento de Inglês: Leitura')
            idioma_escrita = trat_coluna('IDIOMAS - Conhecimento de Inglês: Escrita')
            idioma_fala = trat_coluna('IDIOMAS - Conhecimento de Inglês: Fala')
            idioma_outras = trat_coluna('IDIOMAS - Conhecimento de outras línguas')

            #print na tela
            st.write(f'**Qual o conhecimento de Inglês - Leitura?** {idioma_leitura}')
            st.write(f'**Qual o conhecimento de Inglês - Escrita?** {idioma_escrita}')
            st.write(f'**Qual o conhecimento de Inglês - Fala?** {idioma_fala}')
            st.write(f'**Qual o conhecimento de Inglês - Entendimento?** {idioma_entend}')
            st.write(f'**Faz curso de Inglês?** {idioma_curso}')
            st.write(f'**Conhece outras línguas?** {idioma_outras}')
        
        col1, col2 = st.columns(2,gap='small')
        with col1:
            st.markdown("<h2 style= 'text-align: center'> Desejos de carreira </h2>", unsafe_allow_html=True)

            #variáveis
            carreira_area = trat_coluna('CARREIRA - Área de conhecimento pretendida')
            carreira_apoiada = trat_coluna('CARREIRA - Curso apoiado')
            carreira_outro = trat_coluna('CARREIRA - Curso outros')
            carreira_fora = trat_coluna('CARREIRA - Interesse em estudar fora')

            #print na tela
            st.write(f'**Qual a área do conhecimento que pretende estudar?** {carreira_area}')
            st.write(f'**Qual o curso que pretende estudar - Entre as carreiras apoiadas?** {carreira_apoiada}')
            st.write(f'**Qual o curso que pretende estudar - Entre os cursos apoiados?** {carreira_outro}') 
            st.write(f'**Gostaria de estudar fora do país?** {carreira_fora}')              
 
    with tab7:
        if serie == '8º EF' or serie == '9º EF':
            st.subheader('Khan Academy')
            prog_khan = int(df_selection['8º EF e 9º EF - PROGRESSO KHAN ACADEMY'].values[0])

            id_khan = trat_coluna('ID Khan')

            st.metric('Login Khan', value = id_khan)
            st.metric('% Progresso Khan',value = prog_khan)
        elif serie == "1º EM":
            col1, col2 = st.columns(2,gap='small')
            with col1: #Bolsa Talento 2022-2023
                st.markdown("<h2 style= 'text-align: center'> Bolsa Talento 2022 (Ingresso em 2023) </h2>", unsafe_allow_html=True)

                bt_confirmacao = str(df_selection['Inscrição no BT confirmada'].values[0])
                bt_confirmacao = nulo_vazio(bt_confirmacao)
                bt_realiz_pd = str(df_selection['Prova Digital - Realização da prova'].values[0])
                bt_pd_li = round(df_selection['Prova Digital - Linguagens'].values[0])
                bt_pd_ma1 = round(df_selection['Prova Digital - Matemática 1'].values[0])
                bt_pd_ma2 = round(df_selection['Prova Digital - Matemática 2'].values[0])
                bt_pd_ma3 = round(df_selection['Prova Digital - Matemática 3'].values[0])
                bt_pd_ma23 = round(df_selection['Prova Digital - Matemática 23'].values[0])
                bt_inscricao_id = str(df_selection['ID Cadastro'].values[0])
                bt_chamada = str(df_selection['Chamada'].values[0])
                bt_aval_socio = str(df_selection['Avaliação Socioeconômica'].values[0])
                bt_desafio_ismart = str(df_selection['Desafio Ismart'].values[0])
                bt_entrev_familiar = str(df_selection['Entrevista Familiar'].values[0])
                bt_entrev_individual = str(df_selection['Entrevista Individual'].values[0])
                bt_aprovacao = str(df_selection['Aprovação BT'].values[0])

                if bt_confirmacao != 'Sim':
                    st.write(f'**Inscrição Confirmada:** {bt_confirmacao}')
                elif bt_realiz_pd == 'Não iniciada':
                    st.write(f'**Inscrição Confirmada:** {bt_confirmacao}')
                    st.write(f'**ID inscrição:** {bt_confirmacao}')
                    st.write(f'**Realização da Prova Digital:** {bt_realiz_pd}')
                elif bt_chamada == "-":
                    st.write(f'**Inscrição Confirmada:** {bt_confirmacao}')
                    st.write(f'**ID inscrição:** {bt_confirmacao}')
                    st.write(f'**Realização da Prova Digital:** {bt_realiz_pd}')
                    st.write(f'**Chamada:** Reprovado Prova Digital, não foi convocado para a Maratona de Etapas')
                    st.metric('Nota Prova Digital - Linguagens:', value = bt_pd_li)
                    st.metric('Nota Prova Digital - Matemática 1:', value = bt_pd_ma1)
                    st.metric('Nota Prova Digital - Matemática 2:', value = bt_pd_ma2)
                    st.metric('Nota Prova Digital - Matemática 3:', value = bt_pd_ma3)
                    st.metric('Nota Prova Digital - Matemática 23:', value = bt_pd_ma23)
                else:
                    st.write(f'**Inscrição Confirmada:** {bt_confirmacao}')
                    st.write(f'**ID inscrição:** {bt_confirmacao}')
                    st.write(f'**Realização da Prova Digital:** {bt_realiz_pd}')
                    st.write(f'**Chamada:** {bt_chamada}')
                    st.write(f'**Avaliação Socioeconômica:** {bt_aval_socio}')
                    st.write(f'**Desafio Ismart:** {bt_desafio_ismart}')
                    st.write(f'**Entrevista Familiar:** {bt_entrev_familiar}')
                    st.write(f'**Entrevista Individual:** {bt_entrev_individual}')
                    st.metric('Nota Prova Digital - Linguagens:', value = bt_pd_li)
                    st.metric('Nota Prova Digital - Matemática 1:', value = bt_pd_ma1)
                    st.metric('Nota Prova Digital - Matemática 2:', value = bt_pd_ma2)
                    st.metric('Nota Prova Digital - Matemática 3:', value = bt_pd_ma3)
                    st.metric('Nota Prova Digital - Matemática 23:', value = bt_pd_ma23)

    hide_st_style="""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-9s5bis {visibility: visible;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
