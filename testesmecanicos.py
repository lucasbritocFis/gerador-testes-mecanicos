import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime
import matplotlib.pyplot as plt

# Configuração inicial da página
st.set_page_config(page_title="Testes de Tamanhos de Campo", layout="wide", page_icon="📏")

st.markdown("<h1 style='text-align: center; color: #1e90ff;'>Testes de Tamanhos de Campo</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Realize os testes simétricos e assimétricos e gere o relatório em PDF</p>", unsafe_allow_html=True)

# Função para criar gráfico do teste simétrico
def criar_grafico_campo_simetrico(expected, measured):
    fig, ax = plt.subplots(figsize=(5, 5))
    escala = 0.1  # fator de conversão para visualização

    width_exp = expected["x"] * escala
    height_exp = expected["y"] * escala
    width_meas = measured["x"] * escala
    height_meas = measured["y"] * escala

    # Retângulo esperado (azul)
    ax.add_patch(plt.Rectangle((-width_exp/2, -height_exp/2), width_exp, height_exp,
                               fill=False, edgecolor="blue", lw=2, label="Padrão"))
    # Retângulo medido (vermelho)
    ax.add_patch(plt.Rectangle((-width_meas/2, -height_meas/2), width_meas, height_meas,
                               fill=False, edgecolor="red", lw=2, label="Medido"))
    # Área de tolerância (verde tracejado)
    tol = 0.2 * escala
    ax.add_patch(plt.Rectangle((-width_exp/2 - tol, -height_exp/2 - tol),
                               width_exp + 2*tol, height_exp + 2*tol,
                               fill=False, edgecolor="green", linestyle="--", lw=2, label="Tolerância (±2 mm)"))
    ax.set_title(f"Campo {expected['x']}x{expected['y']} cm")
    lim = max(width_exp, width_meas, height_exp, height_meas) / 2 + tol + 0.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.grid(True)
    ax.legend(loc="upper right")
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

# Função para criar gráfico do teste assimétrico
def criar_grafico_campo_assimetrico(expected, measured):
    fig, ax = plt.subplots(figsize=(5, 5))
    escala = 0.1  # fator de conversão para visualização

    width_exp = (expected["x2"] - expected["x1"]) * escala
    height_exp = (expected["y2"] - expected["y1"]) * escala
    width_meas = (measured["x2"] - measured["x1"]) * escala
    height_meas = (measured["y2"] - measured["y1"]) * escala

    # Centraliza os retângulos
    x0_exp = -width_exp/2
    y0_exp = -height_exp/2
    x0_meas = -width_meas/2
    y0_meas = -height_meas/2

    # Desenha retângulo esperado (azul)
    ax.add_patch(plt.Rectangle((x0_exp, y0_exp), width_exp, height_exp,
                               fill=False, edgecolor="blue", lw=2, label="Padrão"))
    # Desenha retângulo medido (vermelho)
    ax.add_patch(plt.Rectangle((x0_meas, y0_meas), width_meas, height_meas,
                               fill=False, edgecolor="red", lw=2, label="Medido"))
    # Tolerância (±0.2 cm)
    tol = 0.2 * escala
    ax.add_patch(plt.Rectangle((x0_exp - tol, y0_exp - tol),
                               width_exp + 2*tol, height_exp + 2*tol,
                               fill=False, edgecolor="green", linestyle="--", lw=2, label="Tolerância (±2 mm)"))
    ax.set_title("Teste Assimétrico")
    lim = max(width_exp, width_meas, height_exp, height_meas) / 2 + tol + 0.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.grid(True)
    ax.legend(loc="upper right")
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

# Função para gerar o relatório PDF com os testes simétricos e assimétricos
def gerar_relatorio_pdf(dados_simetricos, dados_assimetricos):
    buffer_pdf = io.BytesIO()
    c = canvas.Canvas(buffer_pdf, pagesize=letter)
    width, height = letter

    # Cabeçalho do PDF
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(60, height - 50, "Relatório de Testes de Tamanhos de Campo")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.line(60, height - 80, width - 60, height - 80)
    y = height - 120

    # Seção: Testes Simétricos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y, "Testes Simétricos")
    y -= 20
    for campo, info in dados_simetricos.items():
        expected = info["expected"]
        measured = info["measured"]
        c.setFont("Helvetica", 12)
        c.drawString(60, y, f"Campo {campo}: Padrão: x = {expected['x']} cm, y = {expected['y']} cm")
        c.drawString(300, y, f"Medido: x = {measured['x']} cm, y = {measured['y']} cm")
        tol_sym = (expected['x'] - 0.2 <= measured['x'] <= expected['x'] + 0.2) and \
                  (expected['y'] - 0.2 <= measured['y'] <= expected['y'] + 0.2)
        c.setFillColor(colors.green if tol_sym else colors.red)
        c.drawString(500, y, f"{'Dentro' if tol_sym else 'Fora'} da tolerância (±2 mm)")
        c.setFillColor(colors.black)
        y -= 20
        grafico_sym = criar_grafico_campo_simetrico(expected, measured)
        img_sym = ImageReader(grafico_sym)
        c.drawImage(img_sym, 60, y - 200, width=200, height=200)
        y -= 220
        if y < 150:
            c.showPage()
            y = height - 100

    # Seção: Testes Assimétricos
    c.showPage()
    y = height - 100
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y, "Testes Assimétricos")
    y -= 20
    c.setFont("Helvetica", 12)
    std_asym = dados_assimetricos["std"]
    meas_asym = dados_assimetricos["meas"]
    c.drawString(60, y, f"Padrão: x1 = {std_asym['x1']} cm, x2 = {std_asym['x2']} cm, y1 = {std_asym['y1']} cm, y2 = {std_asym['y2']} cm")
    c.drawString(60, y - 15, f"Medido: x1 = {meas_asym['x1']} cm, x2 = {meas_asym['x2']} cm, y1 = {meas_asym['y1']} cm, y2 = {meas_asym['y2']} cm")
    tol_asym = (std_asym['x1'] - 0.2 <= meas_asym['x1'] <= std_asym['x1'] + 0.2 and
                std_asym['x2'] - 0.2 <= meas_asym['x2'] <= std_asym['x2'] + 0.2 and
                std_asym['y1'] - 0.2 <= meas_asym['y1'] <= std_asym['y1'] + 0.2 and
                std_asym['y2'] - 0.2 <= meas_asym['y2'] <= std_asym['y2'] + 0.2)
    c.setFillColor(colors.green if tol_asym else colors.red)
    c.drawString(500, y, f"{'Dentro' if tol_asym else 'Fora'} da tolerância (±2 mm)")
    c.setFillColor(colors.black)
    y -= 20
    grafico_asym = criar_grafico_campo_assimetrico(std_asym, meas_asym)
    img_asym = ImageReader(grafico_asym)
    c.drawImage(img_asym, 60, y - 200, width=200, height=200)
    
    c.setFont("Helvetica", 10)
    c.drawString(60, 40, "Gerado por Streamlit - Testes de Tamanhos de Campo")
    c.drawString(width - 100, 40, "Página 1")
    c.save()
    buffer_pdf.seek(0)
    return buffer_pdf

# Criação das abas para separar os testes
tabs = st.tabs(["Testes Simétricos", "Testes Assimétricos"])

# Aba: Testes Simétricos
with tabs[0]:
    st.markdown("### Testes Simétricos")
    tamanhos = [5, 10, 15, 20, 25]
    dados_simetricos = {}
    for tamanho in tamanhos:
        st.markdown(f"#### Campo {tamanho}x{tamanho}")
        col1, col2 = st.columns(2)
        with col1:
            meas_x = st.number_input(f"Medido x ({tamanho}x{tamanho})", key=f"meas_x_{tamanho}", value=float(tamanho), step=0.1)
        with col2:
            meas_y = st.number_input(f"Medido y ({tamanho}x{tamanho})", key=f"meas_y_{tamanho}", value=float(tamanho), step=0.1)
        dados_simetricos[f"{tamanho}x{tamanho}"] = {
            "expected": {"x": tamanho, "y": tamanho},
            "measured": {"x": meas_x, "y": meas_y}
        }
        st.markdown("---")

# Aba: Testes Assimétricos
with tabs[1]:
    st.markdown("### Testes Assimétricos")
    st.markdown("#### Linha 1 (Padrão)")
    col_std, sep_std, col_std2 = st.columns([2, 1, 2])
    with col_std:
        std_x1 = st.number_input("Padrão - x1 (cm)", key="std_x1", value=0.0, step=0.1)
    with col_std2:
        std_x2 = st.number_input("Padrão - x2 (cm)", key="std_x2", value=10.0, step=0.1)
    col_std3, col_std4 = st.columns([2, 2])
    with col_std3:
        std_y1 = st.number_input("Padrão - y1 (cm)", key="std_y1", value=0.0, step=0.1)
    with col_std4:
        std_y2 = st.number_input("Padrão - y2 (cm)", key="std_y2", value=10.0, step=0.1)

    st.markdown("#### Linha 2 (Medido)")
    col_meas, sep_meas, col_meas2 = st.columns([2, 1, 2])
    with col_meas:
        meas_x1 = st.number_input("Medido - x1 (cm)", key="meas_x1", value=0.1, step=0.1)
    with col_meas2:
        meas_x2 = st.number_input("Medido - x2 (cm)", key="meas_x2", value=9.9, step=0.1)
    col_meas3, col_meas4 = st.columns([2, 2])
    with col_meas3:
        meas_y1 = st.number_input("Medido - y1 (cm)", key="meas_y1", value=0.2, step=0.1)
    with col_meas4:
        meas_y2 = st.number_input("Medido - y2 (cm)", key="meas_y2", value=10.1, step=0.1)
    
    dados_assimetricos = {
        "std": {"x1": std_x1, "x2": std_x2, "y1": std_y1, "y2": std_y2},
        "meas": {"x1": meas_x1, "x2": meas_x2, "y1": meas_y1, "y2": meas_y2}
    }

# Botão para gerar o relatório PDF com ambos os testes
if st.button("Gerar Relatório Completo"):
    with st.spinner("Gerando relatório..."):
        pdf_buffer = gerar_relatorio_pdf(dados_simetricos, dados_assimetricos)
        st.success("Relatório gerado com sucesso!")
        st.download_button(
            label="Baixar Relatório",
            data=pdf_buffer,
            file_name="Relatorio_Tamanhos_Campo.pdf",
            mime="application/pdf"
        )
