import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from functools import reduce
from io import BytesIO
from st_pages import Page, Section, add_page_title, show_pages



st.set_page_config(page_title = "Dash 360 IOL 2023", layout="wide", initial_sidebar_state="collapsed")

show_pages(
    [
        Page("pages/leia_me.py", "Leia Me", ":books:"),
        #Page("pages/painel_metas.py", "Painel de Metas", ":dart:"), [[AJUSTAR]]
        Page("dash_streamlit.py", "Dash Macro", ":bar_chart:"),
        Page("pages/dash_micro.py", "Dash Micro", ":female-student:"),
        Page("pages/filtro_base.py", "Filtro e Download Base", ":pushpin:"),
        Page("pages/one_page.py", "Informações Gerais e Históricas", ":1234:"),
    ]
)