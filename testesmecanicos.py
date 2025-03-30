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
st.markdown("<h3 style='text-align: center;'>Teste para o tamanho de campo simétrico   Teste para o tamanho de campo assimétrico</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Linha 1 = Padrão | Linha 2 = Medido</p>", unsafe_allow_html=True)

# =============================
# Interface – Linha 1 (Padrão)
# =============================
st.write("### Linha 1 (Padrão)")
# Divisão em 3 colunas: simétrico, separador e assimétrico
col_sym1, col_sep1, col_asym1 = st.columns([2, 1, 2])
with col_sym1:
    sym1_cols = st.columns(2)
    std_sym_x = sym1_cols[0].number_input("Simétrico: x (cm)", key="std_sym_x", value=5.0)
    std_sym_y = sym1_cols[1].number_input("Simétrico: y (cm)", key="std_sym_y", value=5.0)
with col_asym1:
    # Para o teste assimétrico, separe em duas linhas: primeira para x1 e x2, segunda para y1 e y2
    asym1_top = st.columns(2)
    std_asym_x1 = asym1_top[0].number_input("Assimétrico: x1 (cm)", key="std_asym_x1", value=0.0)
    std_asym_x2 = asym1_top[1].number_input("Assimétrico: x2 (cm)", key="std_asym_x2", value=10.0)
    asym1_bot = st.columns(2)
    std_asym_y1 = asym1_bot[0].number_input("Assimétrico: y1 (cm)", key="std_asym_y1", value=0.0)
    std_asym_y2 = asym1_bot[1].number_input("Assimétrico: y2 (cm)", key="std_asym_y2", value=10.0)

st.markdown("---")

# =============================
# Interface – Linha 2 (Medido)
# =============================
st.write("### Linha 2 (Medido)")
col_sym2, col_sep2, col_asym2 = st.columns([2, 1, 2])
with col_sym2:
    sym2_cols = st.columns(2)
    meas_sym_x = sym2_cols[0].number_input("Simétrico: x (cm)", key="meas_sym_x", value=5.2)
    meas_sym_y = sym2_cols[1].number_input("Simétrico: y (cm)", key="meas_sym_y", value=4.9)

with col_asym2:
    asym2_top = st.columns(2)
    meas_asym_x1 = asym2_top[0].number_input("Assimétrico: x1 (cm)", key="meas_asym_x1", value=0.1)
    meas_asym_x2 = asym2_top[1].number_input("Assimétrico: x2 (cm)", key="meas_asym_x2", value=9.9)
    asym2_bot = st.columns(2)
    meas_asym_y1 = asym2_bot[0].number_input("Assimétrico: y1 (cm)", key="meas_asym_y1", value=0.2)
    meas_asym_y2 = asym2_bot[1].number_input("Assimétrico: y2 (cm)", key="meas_asym_y2", value=10.1)

# Função para criar gráfico do teste simétrico
def criar_grafico_campo_simetrico(expected, measured):
    # expected e measured são dicionários com chaves "x" e "y"
    fig, ax = plt.subplots(figsize=(5, 5))
    escala = 0.1  # escala para visualização (cm -> plot)
    # Define os tamanhos para o retângulo padrão (centrado)
    width_exp = expected["x"] * escala
    height_exp = expected["y"] * escala
    width_meas = measured["x"] * escala
    height_meas = measured["y"] * escala

    # Desenha o retângulo esperado (azul)
    ax.add_patch(plt.Rectangle((-width_exp/2, -height_exp/2), width_exp, height_exp,
                               fill=False, edgecolor="blue", label="Padrão"))
    # Desenha o retângulo medido (vermelho)
    ax.add_patch(plt.Rectangle((-width_meas/2, -height_meas/2), width_meas, height_meas,
                               fill=False, edgecolor="red", label="Medido"))
    # Tolerância (±2 mm -> 0.2 cm)
    tol = 0.2 * escala
    ax.add_patch(plt.Rectangle((-width_exp/2 - tol, -height_exp/2 - tol),
                               width_exp + 2*tol, height_exp + 2*tol,
                               fill=False, edgecolor="green", linestyle="--", label="Tolerância (±2 mm)"))
    ax.set_title("Teste Simétrico")
    lim = max(width_exp, width_meas, height_exp, height_meas) / 2 + tol + 0.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.grid(True)
    ax.legend()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

# Função para criar gráfico do teste assimétrico
def criar_grafico_campo_assimetrico(expected, measured):
    # expected e measured são dicionários com chaves "x1", "x2", "y1", "y2"
    fig, ax = plt.subplots(figsize=(5, 5))
    escala = 0.1  # escala para visualização
    # Calcula largura e altura para o retângulo esperado
    width_exp = (expected["x2"] - expected["x1"]) * escala
    height_exp = (expected["y2"] - expected["y1"]) * escala
    # Define os pontos de início para centralizar a figura
    x0_exp = -width_exp/2
    y0_exp = -height_exp/2
    # Para o retângulo medido
    width_meas = (measured["x2"] - measured["x1"]) * escala
    height_meas = (measured["y2"] - measured["y1"]) * escala
    x0_meas = -width_meas/2
    y0_meas = -height_meas/2

    # Desenha o retângulo esperado (azul)
    ax.add_patch(plt.Rectangle((x0_exp, y0_exp), width_exp, height_exp,
                               fill=False, edgecolor="blue", label="Padrão"))
    # Desenha o retângulo medido (vermelho)
    ax.add_patch(plt.Rectangle((x0_meas, y0_meas), width_meas, height_meas,
                               fill=False, edgecolor="red", label="Medido"))
    # Tolerância
    tol = 0.2 * escala
    ax.add_patch(plt.Rectangle((x0_exp - tol, y0_exp - tol),
                               width_exp + 2*tol, height_exp + 2*tol,
                               fill=False, edgecolor="green", linestyle="--", label="Tolerância (±2 mm)"))
    ax.set_title("Teste Assimétrico")
    lim = max(width_exp, width_meas, height_exp, height_meas) / 2 + tol + 0.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.grid(True)
    ax.legend()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

# Função para gerar o relatório em PDF
def gerar_relatorio_pdf(std_sym, meas_sym, std_asym, meas_asym):
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

    # Seção – Teste Simétrico
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y, "Teste de Tamanho de Campo Simétrico")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"Padrão: x = {std_sym['x']} cm, y = {std_sym['y']} cm")
    c.drawString(300, y, f"Medido: x = {meas_sym['x']} cm, y = {meas_sym['y']} cm")
    # Verifica tolerância (±0.2 cm)
    tol_sym = (std_sym['x'] - 0.2 <= meas_sym['x'] <= std_sym['x'] + 0.2) and (std_sym['y'] - 0.2 <= meas_sym['y'] <= std_sym['y'] + 0.2)
    c.setFillColor(colors.green if tol_sym else colors.red)
    c.drawString(500, y, f"{'Dentro' if tol_sym else 'Fora'} da tolerância (±2 mm)")
    c.setFillColor(colors.black)
    y -= 20
    # Insere gráfico do teste simétrico
    grafico_sym = criar_grafico_campo_simetrico(std_sym, meas_sym)
    img_sym = ImageReader(grafico_sym)
    c.drawImage(img_sym, 60, y - 200, width=200, height=200)
    y -= 220

    # Seção – Teste Assimétrico
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y, "Teste de Tamanho de Campo Assimétrico")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"Padrão: x1 = {std_asym['x1']}, x2 = {std_asym['x2']}, y1 = {std_asym['y1']}, y2 = {std_asym['y2']} cm")
    c.drawString(60, y - 15, f"Medido: x1 = {meas_asym['x1']}, x2 = {meas_asym['x2']}, y1 = {meas_asym['y1']}, y2 = {meas_asym['y2']} cm")
    # Verifica tolerância para cada parâmetro
    tol_asym = (std_asym['x1'] - 0.2 <= meas_asym['x1'] <= std_asym['x1'] + 0.2 and
                std_asym['x2'] - 0.2 <= meas_asym['x2'] <= std_asym['x2'] + 0.2 and
                std_asym['y1'] - 0.2 <= meas_asym['y1'] <= std_asym['y1'] + 0.2 and
                std_asym['y2'] - 0.2 <= meas_asym['y2'] <= std_asym['y2'] + 0.2)
    c.setFillColor(colors.green if tol_asym else colors.red)
    c.drawString(500, y, f"{'Dentro' if tol_asym else 'Fora'} da tolerância (±2 mm)")
    c.setFillColor(colors.black)
    y -= 20
    # Insere gráfico do teste assimétrico
    grafico_asym = criar_grafico_campo_assimetrico(std_asym, meas_asym)
    img_asym = ImageReader(grafico_asym)
    c.drawImage(img_asym, 60, y - 200, width=200, height=200)
    
    # Rodapé
    c.setFont("Helvetica", 10)
    c.drawString(60, 40, "Gerado por Streamlit - Testes de Tamanhos de Campo")
    c.drawString(width - 100, 40, "Página 1")
    c.save()
    buffer_pdf.seek(0)
    return buffer_pdf

# Prepara os dicionários com os dados informados
dados_std_simetrico = {"x": std_sym_x, "y": std_sym_y}
dados_meas_simetrico = {"x": meas_sym_x, "y": meas_sym_y}
dados_std_assimetrico = {"x1": std_asym_x1, "x2": std_asym_x2, "y1": std_asym_y1, "y2": std_asym_y2}
dados_meas_assimetrico = {"x1": meas_asym_x1, "x2": meas_asym_x2, "y1": meas_asym_y1, "y2": meas_asym_y2}

# Botão para gerar relatório
if st.button("Gerar Relatório"):
    with st.spinner("Gerando relatório..."):
        pdf_buffer = gerar_relatorio_pdf(dados_std_simetrico, dados_meas_simetrico,
                                         dados_std_assimetrico, dados_meas_assimetrico)
        st.success("Relatório gerado com sucesso!")
        st.download_button(
            label="Baixar Relatório",
            data=pdf_buffer,
            file_name="Relatorio_Tamanhos_Campo.pdf",
            mime="application/pdf"
        )
