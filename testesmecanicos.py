import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
from datetime import datetime

# Configuração inicial do Streamlit com layout moderno
st.set_page_config(page_title="Gerador de Relatórios Mecânicos", layout="wide", page_icon="⚙️")
st.markdown("""
    <style>
    .main {background-color: #f0f2f6;}
    .stButton>button {
        background-color: #1e90ff;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #4169e1;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stTextInput>div>input, .stNumberInput>div>input {
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #dcdcdc;
        background-color: #ffffff;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #1e90ff;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 18px;
        color: #555555;
        text-align: center;
        margin-bottom: 40px;
    }
    .section-header {
        font-size: 24px;
        color: #333333;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Função para gerar o PDF
def gerar_relatorio_pdf(dados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Cabeçalho
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(60, height - 50, "Relatório de Testes Mecânicos")
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.line(60, height - 80, width - 60, height - 80)

    # Dados Gerais
    y = height - 120
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y, "Dados Gerais")
    y -= 20
    c.setFont("Helvetica", 12)
    for chave, valor in dados["gerais"].items():
        c.drawString(60, y, f"{chave}: {valor}")
        y -= 20

    # Parâmetros de Posicionamento
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y, "Parâmetros de Posicionamento")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"X1: {dados['posicionamento']['x1']} cm")
    c.drawString(200, y, f"X2: {dados['posicionamento']['x2']} cm")
    y -= 20
    c.drawString(60, y, f"Y1: {dados['posicionamento']['y1']} cm")
    c.drawString(200, y, f"Y2: {dados['posicionamento']['y2']} cm")

    # Parâmetros Mecânicos
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y, "Parâmetros Mecânicos")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"Gantry: {dados['mecanicos']['gantry']}°")
    c.drawString(200, y, f"Colimador: {dados['mecanicos']['colimador']}°")
    c.drawString(340, y, f"Mesa: {dados['mecanicos']['mesa']}°")
    y -= 20
    c.drawString(60, y, f"Deslocamento Lateral: {dados['mecanicos']['desloc_lateral']} cm")
    c.drawString(200, y, f"Deslocamento Vertical: {dados['mecanicos']['desloc_vertical']} cm")
    c.drawString(340, y, f"Deslocamento Longitudinal: {dados['mecanicos']['desloc_longitudinal']} cm")

    # Rodapé
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 10)
    c.drawString(60, 40, "Gerado por Streamlit - Testes Mecânicos")
    c.drawString(width - 100, 40, f"Página 1")

    c.save()
    buffer.seek(0)
    return buffer

# Interface do Streamlit
st.markdown('<div class="title">⚙️ Gerador de Relatórios Mecânicos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Insira os parâmetros abaixo para criar um relatório personalizado</div>', unsafe_allow_html=True)

# Formulário para entrada de dados
with st.form(key="form_testes_mecanicos"):
    st.markdown('<div class="section-header">Dados Gerais</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nome_teste = st.text_input("Nome do Teste", "Teste Mecânico 01")
        responsavel = st.text_input("Responsável", "João Silva")
    with col2:
        equipamento = st.text_input("Equipamento", "Máquina XYZ")
        data_teste = st.date_input("Data do Teste", datetime.now())

    st.markdown('<div class="section-header">Parâmetros de Posicionamento</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        x1 = st.number_input("X1 (cm)", min_value=-100.0, max_value=100.0, value=0.0, step=0.1)
        y1 = st.number_input("Y1 (cm)", min_value=-100.0, max_value=100.0, value=0.0, step=0.1)
    with col4:
        x2 = st.number_input("X2 (cm)", min_value=-100.0, max_value=100.0, value=0.0, step=0.1)
        y2 = st.number_input("Y2 (cm)", min_value=-100.0, max_value=100.0, value=0.0, step=0.1)

    st.markdown('<div class="section-header">Parâmetros Mecânicos</div>', unsafe_allow_html=True)
    col5, col6, col7 = st.columns(3)
    with col5:
        gantry = st.number_input("Gantry (°)", min_value=0.0, max_value=360.0, value=0.0, step=1.0)
        desloc_lateral = st.number_input("Deslocamento Lateral (cm)", min_value=-50.0, max_value=50.0, value=0.0, step=0.1)
    with col6:
        colimador = st.number_input("Colimador (°)", min_value=0.0, max_value=360.0, value=0.0, step=1.0)
        desloc_vertical = st.number_input("Deslocamento Vertical (cm)", min_value=-50.0, max_value=50.0, value=0.0, step=0.1)
    with col7:
        mesa = st.number_input("Mesa (°)", min_value=0.0, max_value=360.0, value=0.0, step=1.0)
        desloc_longitudinal = st.number_input("Deslocamento Longitudinal (cm)", min_value=-50.0, max_value=50.0, value=0.0, step=0.1)

    # Botão para gerar o relatório
    submit_button = st.form_submit_button(label="Gerar Relatório")

# Processamento do formulário
if submit_button:
    with st.spinner("Gerando o relatório..."):
        dados = {
            "gerais": {
                "Nome do Teste": nome_teste,
                "Responsável": responsavel,
                "Equipamento": equipamento,
                "Data do Teste": data_teste.strftime("%d/%m/%Y")
            },
            "posicionamento": {
                "x1": x1,
                "x2": x2,
                "y1": y1,
                "y2": y2
            },
            "mecanicos": {
                "gantry": gantry,
                "colimador": colimador,
                "mesa": mesa,
                "desloc_lateral": desloc_lateral,
                "desloc_vertical": desloc_vertical,
                "desloc_longitudinal": desloc_longitudinal
            }
        }
        pdf_buffer = gerar_relatorio_pdf(dados)
        st.success("Relatório gerado com sucesso!")
        st.download_button(
            label="Baixar Relatório",
            data=pdf_buffer,
            file_name=f"Relatorio_Mecanico_{nome_teste.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

# Rodapé
st.markdown("""
    <hr style="border: 1px solid #dcdcdc;">
    <p style="text-align: center; color: #777777;">Desenvolvido com Streamlit • 2025</p>
""", unsafe_allow_html=True)
