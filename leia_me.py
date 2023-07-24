import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from functools import reduce
import io
from io import BytesIO

favicon = Image.open("favicon.ico")

st.set_page_config(page_title = "Leia-me", layout="wide")
st.title("Bem-vindo/a!")
st.subheader("Seja bem-vindo(a) aos Dash 360 do Ismart Online :star2:")
st.markdown("Para navegar entre os dashs, utilize o menu lateral. Para visualizar as informações, basta inserir usuário e senha.")
st.markdown("Dentro do **Dash Macro**, é possível filtrar os dados via menu lateral, sendo também possível baixar a base de dados, contendo as informações de acordo com o filtro selecionado.")
st.markdown("Dentro do **Dash Micro**, é possível filtrar os dados via caixa de seleção no início da própria página, contendo as informações de acordo com o aluno selecionado.")
st.markdown("Na aba **Filtro e Download Base**, é possível filtrar todos os dados e selecionar as colunas no início da própria página, a fim de baixar a base de dados de acordo com os filtros.")

st.markdown("Atualizações e/ou inserções de informação nos dashs serão sempre informados via esta página.")
st.markdown("Para dúvidas, sugestões, alteração de senha, entre outros: julia.tolentino@ismart.org.br :email:")

st.subheader("Atualizações fixas:")
st.markdown(":white_check_mark: 19/06 - Status e Dados Cadastrais;")
st.markdown(":white_check_mark: 19/06 - Engajamento 2023;")
st.markdown(":white_check_mark: 23/05 - Olimpíadas;")
st.markdown("##")

st.subheader("Inserção de informações:")
st.markdown(":white_check_mark: 13/03/23 - Última atualização Progresso Khan Academy (8º EF - 08/03; 9º EF - 12/03);")
st.markdown(":white_check_mark: 27/02/23 - Última atualização ENEM 2022;")
st.markdown(":white_check_mark: 27/02/23 - Tab e gráficos de Khan Academy no Dash Macro;")
st.markdown(":white_check_mark: 14/02/23 - Tab e gráficos de ENEM 2022 no Dash Macro;")
st.markdown(":white_check_mark: 13/02/23 - Login e Progresso de Khan Academy no dash Micro;")
st.markdown(":white_check_mark: 09/02/23 - 8º EF: Finalização da assinatura de contrato;")
st.markdown(":white_check_mark: 24/01/23 - Estudantes aprovados no BT 2023 foram retirados da base;")
st.markdown(":white_check_mark: 16/01/23 - Tab de sinalizações/flags no Dash Micro;")
st.markdown(":white_check_mark: 16/01/23 - Aba de filtro;")
st.markdown(":white_check_mark: 16/01/23 - Informações de 2023;")
st.markdown(":white_check_mark: 13/12/22 - Cálculo de total de engajamento ajustado (contabiliza formações);")
st.markdown(":white_check_mark: 07/12/22 - Notas PU 3 9º EF, Presença e Justificativa na 4ª Formação;")
st.markdown(":white_check_mark: 06/12/22 - Dashboards liberados")


hide_st_style="""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .css-9s5bis {visibility: visible;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)
