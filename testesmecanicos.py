import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
from datetime import datetime
import matplotlib.pyplot as plt
import tempfile

# Configuração inicial do Streamlit
st.set_page_config(page_title="Testes de Tamanhos de Campo", layout="wide", page_icon="📏")
st.markdown("""
    <style>
    /* --- ESTILO MINIMALISTA AZUL --- */
    .main {
        background-color: #f0f8ff;  /* Azul bem claro */
    }
    
    /* Inputs numéricos compactos */
    .stNumberInput>div>div>input {
        width: 10px !important;
        min-width: 10px !important;
        padding: 4px 8px !important;
        margin: 0 !important;
        border: 1px solid #add8e6 !important;  /* Azul claro */
        border-radius: 6px !important;
        background-color: #ffffff !important;
        font-size: 12px !important;
    }
    
    /* Container dos inputs */
    .stNumberInput>div>div {
        width: 30px !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Botões + e - */
    .stNumberInput>div>div>div>button {
        width: 20px !important;
        height: 20px !important;
        padding: 0 !important;
        margin: 0 2px !important;
        border: none !important;
        background-color: #add8e6 !important;  /* Azul claro */
        color: #00008b !important;  /* Azul escuro */
        border-radius: 4px !important;
    }
    
    /* Botão principal */
    .stButton>button {
        background-color: #4682b4 !important;  /* Azul médio */
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-size: 14px !important;
    }
    
    /* Títulos */
    .title {
        color: #000080 !important;  /* Azul marinho */
        font-size: 28px !important;
    }
    
    /* Linha divisória */
    hr {
        border: 1px solid #4682b4 !important;  /* Azul médio */
    }
    </style>
""", unsafe_allow_html=True)

# [Mantenha todas as suas funções existentes: criar_grafico_campo, gerar_relatorio_pdf]

# Interface do Streamlit
st.markdown('<div class="title">📏 Testes de Tamanhos de Campo</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#4682b4; text-align:center;">Insira os valores medidos para gerar um relatório</div>', unsafe_allow_html=True)

# Divisão em colunas (mantenha o mesmo layout)
col1, col2 = st.columns(2)
dados_simetricos = {}
dados_assimetricos = {}

# Testes Simétricos
with col1:
    st.markdown('<div style="color:#000080; font-weight:bold;">Campos Simétricos</div>', unsafe_allow_html=True)
    for tamanho in [5, 10, 15, 20, 25]:
        st.write(f"**Campo {tamanho}x{tamanho} cm**")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            x = st.number_input(f"X ({tamanho}x{tamanho})", min_value=0.0, max_value=30.0, value=float(tamanho), step=0.1, key=f"x_{tamanho}")
        with subcol2:
            y = st.number_input(f"Y ({tamanho}x{tamanho})", min_value=0.0, max_value=30.0, value=float(tamanho), step=0.1, key=f"y_{tamanho}")
        dados_simetricos[f"{tamanho}x{tamanho}"] = {"x": x, "y": y}

# Testes Assimétricos (mantenha a mesma estrutura)

# Botão para gerar relatório
if st.button("Gerar Relatório PDF", key="pdf_button"):
    with st.spinner("Gerando relatório..."):
        pdf_buffer = gerar_relatorio_pdf(dados_simetricos, dados_assimetricos)
        st.success("Pronto!")
        st.download_button(
            label="⬇️ Baixar Relatório",
            data=pdf_buffer,
            file_name=f"Relatorio_Campos_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

st.markdown("---")
st.markdown('<div style="text-align:center; color:#4682b4;">Desenvolvido com Streamlit</div>', unsafe_allow_html=True)
