
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
    .main {background-color: #e6f0ff;}
    .stButton>button {
        background-color: #1e90ff;
        color: white;
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: bold;
        width: 120px !important;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #4169e1;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* Ajuste dos campos numéricos */
    .stNumberInput {
        margin: 0px !important;
        padding: 0px !important;
        width: 60px !important;  /* Ajuste a largura conforme necessário */
    }
    .stNumberInput > div {
        margin: 0px !important;
        padding: 0px !important;
    }
    /* Ajuste das colunas */
    [class*="stHorizontal"] > div {
        max-width: 60px !important;  /* Largura máxima das colunas */
        margin-right: 2px !important;
        margin-left: 2px !important;
    }
    /* Remover espaçamento extra */
    .st-emotion-cache-1r4s1i0 {
        margin: 0px !important;
        padding: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Função para criar gráficos
def criar_grafico_campo(padrao, medido, tipo, tamanho=None):
    fig, ax = plt.subplots(figsize=(5, 5))
    escala = 0.1
    if tipo == "simetrico":
        x_padrao, y_padrao = tamanho * escala, tamanho * escala
        x_medido, y_medido = medido["x"] * escala, medido["y"] * escala
        ax.set_title(f"Campo Simétrico {tamanho}x{tamanho} cm")
    else:
        x_padrao = (padrao["x2"] - padrao["x1"]) * escala
        y_padrao = (padrao["y2"] - padrao["y1"]) * escala
        x_medido = (medido["x2"] - medido["x1"]) * escala
        y_medido = (medido["y2"] - medido["y1"]) * escala
        ax.set_title("Campo Assimétrico")
    ax.add_patch(plt.Rectangle((-x_padrao/2, -y_padrao/2), x_padrao, y_padrao, fill=False, color="blue", label="Padrão"))
    ax.add_patch(plt.Rectangle((-x_medido/2, -y_medido/2), x_medido, y_medido, fill=False, color="red", label="Medido"))
    tolerancia = 0.2 * escala
    ax.add_patch(plt.Rectangle((-x_padrao/2 - tolerancia, -y_padrao/2 - tolerancia), 
                               x_padrao + 2 * tolerancia, y_padrao + 2 * tolerancia, 
                               fill=False, color="green", linestyle="--", label="Tolerância (±2 mm)"))
    limite = max(x_padrao, x_medido, y_padrao, y_medido) / 2 + tolerancia + 0.5
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.grid(True)
    ax.legend()
    ax.set_aspect('equal')
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        fig.savefig(tmp.name, format="png", dpi=100)
        caminho = tmp.name
    plt.close(fig)
    return caminho

# Função para gerar o PDF
def gerar_relatorio_pdf(dados_simetricos, dados_assimetricos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(60, height - 50, "Relatório de Testes de Tamanhos de Campo")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.line(60, height - 80, width - 60, height - 80)
    y = height - 120
    if dados_simetricos:
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y, "Testes Simétricos")
        y -= 20
        tamanhos = [5, 10, 15, 20, 25]
        for i, tamanho in enumerate(tamanhos):
            x_medido = dados_simetricos[f"{tamanho}x{tamanho}"]["x"]
            y_medido = dados_simetricos[f"{tamanho}x{tamanho}"]["y"]
            c.setFont("Helvetica", 12)
            c.drawString(60, y, f"Campo {tamanho}x{tamanho} cm: X = {x_medido} cm, Y = {y_medido} cm")
            tolerancia_x = (tamanho - 0.2) <= x_medido <= (tamanho + 0.2)
            tolerancia_y = (tamanho - 0.2) <= y_medido <= (tamanho + 0.2)
            c.setFillColor(tolerancia_x and tolerancia_y and colors.green or colors.red)
            c.drawString(300, y, f"{'Dentro' if tolerancia_x and tolerancia_y else 'Fora'} da tolerância (±2 mm)")
            c.setFillColor(colors.black)
            grafico = criar_grafico_campo(None, {"x": x_medido, "y": y_medido}, "simetrico", tamanho)
            c.drawImage(grafico, 60, y - 150, width=200, height=200)
            y -= 220
    if dados_assimetricos:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y, "Testes Assimétricos")
        y -= 20
        c.setFont("Helvetica", 12)
        c.drawString(60, y, f"Padrão: X1={dados_assimetricos['padrao']['x1']}, X2={dados_assimetricos['padrao']['x2']}, "
                           f"Y1={dados_assimetricos['padrao']['y1']}, Y2={dados_assimetricos['padrao']['y2']} cm")
        y -= 20
        c.drawString(60, y, f"Medido: X1={dados_assimetricos['medido']['x1']}, X2={dados_assimetricos['medido']['x2']}, "
                           f"Y1={dados_assimetricos['medido']['y1']}, Y2={dados_assimetricos['medido']['y2']} cm")
        tolerancia_x1 = (dados_assimetricos['padrao']['x1'] - 0.2) <= dados_assimetricos['medido']['x1'] <= (dados_assimetricos['padrao']['x1'] + 0.2)
        tolerancia_x2 = (dados_assimetricos['padrao']['x2'] - 0.2) <= dados_assimetricos['medido']['x2'] <= (dados_assimetricos['padrao']['x2'] + 0.2)
        tolerancia_y1 = (dados_assimetricos['padrao']['y1'] - 0.2) <= dados_assimetricos['medido']['y1'] <= (dados_assimetricos['padrao']['y1'] + 0.2)
        tolerancia_y2 = (dados_assimetricos['padrao']['y2'] - 0.2) <= dados_assimetricos['medido']['y2'] <= (dados_assimetricos['padrao']['y2'] + 0.2)
        c.setFillColor(all([tolerancia_x1, tolerancia_x2, tolerancia_y1, tolerancia_y2]) and colors.green or colors.red)
        c.drawString(300, y, f"{'Dentro' if all([tolerancia_x1, tolerancia_x2, tolerancia_y1, tolerancia_y2]) else 'Fora'} da tolerância (±2 mm)")
        c.setFillColor(colors.black)
        grafico = criar_grafico_campo(dados_assimetricos["padrao"], dados_assimetricos["medido"], "assimetrico")
        c.drawImage(grafico, 60, y - 150, width=200, height=200)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(60, 40, "Gerado por Streamlit - Testes de Tamanhos de Campo")
    c.drawString(width - 100, 40, f"Página 1")
    c.save()
    buffer.seek(0)
    return buffer

# Interface do Streamlit
st.markdown('<div class="title">📏 Testes de Tamanhos de Campo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Insira os valores medidos para gerar um relatório com representações visuais</div>', unsafe_allow_html=True)

# Divisão em duas colunas principais
col1, col2 = st.columns(2)

dados_simetricos = {}
dados_assimetricos = {}

# Testes Simétricos
with col1:
    st.markdown('<div class="section-header">Campos Simétricos</div>', unsafe_allow_html=True)
    for tamanho in [5, 10, 15, 20, 25]:
        st.write(f"Campo {tamanho}x{tamanho} cm")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            x = st.number_input(f"X", min_value=0.0, max_value=30.0, value=float(tamanho), step=0.1, key=f"x_{tamanho}")
        with subcol2:
            y = st.number_input(f"Y", min_value=0.0, max_value=30.0, value=float(tamanho), step=0.1, key=f"y_{tamanho}")
        dados_simetricos[f"{tamanho}x{tamanho}"] = {"x": x, "y": y}
        st.markdown("<hr style='border: 1px solid #00ff00; margin: 5px 0;' />", unsafe_allow_html=True)

# Testes Assimétricos
with col2:
    st.markdown('<div class="section-header">Campo Assimétrico</div>', unsafe_allow_html=True)
    
    st.write("Padrão")
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        x1_padrao = st.number_input("X1", min_value=-20.0, max_value=20.0, value=0.0, step=0.1, key="x1_padrao")
    with subcol2:
        x2_padrao = st.number_input("X2", min_value=-20.0, max_value=20.0, value=10.0, step=0.1, key="x2_padrao")
    subcol3, subcol4 = st.columns(2)
    with subcol3:
        y1_padrao = st.number_input("Y1", min_value=-20.0, max_value=20.0, value=0.0, step=0.1, key="y1_padrao")
    with subcol4:
        y2_padrao = st.number_input("Y2", min_value=-20.0, max_value=20.0, value=10.0, step=0.1, key="y2_padrao")

    st.write("Medido")
    subcol5, subcol6 = st.columns(2)
    with subcol5:
        x1_medido = st.number_input("X1", min_value=-20.0, max_value=20.0, value=0.0, step=0.1, key="x1_medido")
    with subcol6:
        x2_medido = st.number_input("X2", min_value=-20.0, max_value=20.0, value=10.0, step=0.1, key="x2_medido")
    subcol7, subcol8 = st.columns(2)
    with subcol7:
        y1_medido = st.number_input("Y1", min_value=-20.0, max_value=20.0, value=0.0, step=0.1, key="y1_medido")
    with subcol8:
        y2_medido = st.number_input("Y2", min_value=-20.0, max_value=20.0, value=10.0, step=0.1, key="y2_medido")

    dados_assimetricos = {
        "padrao": {"x1": x1_padrao, "x2": x2_padrao, "y1": y1_padrao, "y2": y2_padrao},
        "medido": {"x1": x1_medido, "x2": x2_medido, "y1": y1_medido, "y2": y2_medido}
    }

# Botão para gerar relatório
if st.button("Gerar Relatório"):
    with st.spinner("Gerando o relatório..."):
        pdf_buffer = gerar_relatorio_pdf(dados_simetricos, dados_assimetricos)
        st.success("Relatório gerado com sucesso!")
        st.download_button(
            label="Baixar Relatório",
            data=pdf_buffer,
            file_name="Relatorio_Tamanhos_Campo.pdf",
            mime="application/pdf"
        )

st.markdown("""
    <hr style="border: 1px solid #00ff00;">
    <p style="text-align: center; color: #ff0000;">Desenvolvido com Streamlit • 2025</p>
""", unsafe_allow_html=True)
