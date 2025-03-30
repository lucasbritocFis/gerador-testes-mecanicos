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

st.markdown("<h1 style='text-align: center; color: #1e90ff;'>Testes de Tamanhos de Campo Simétrico</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>5x5, 10x10, 15x15, 20x20 e 25x25</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Para cada campo, o valor esperado é o próprio tamanho. Insira os valores medidos e gere o relatório.</p>", unsafe_allow_html=True)

# Lista de tamanhos de campo
tamanhos = [5, 10, 15, 20, 25]

# Dicionário para armazenar os dados medidos para cada tamanho
dados_simetricos = {}

# Cria uma seção para cada campo
for tamanho in tamanhos:
    st.markdown(f"### Campo {tamanho}x{tamanho}")
    col1, col2 = st.columns(2)
    with col1:
        medida_x = st.number_input(f"Medido x ({tamanho}x{tamanho})", key=f"meas_x_{tamanho}", value=float(tamanho), step=0.1)
    with col2:
        medida_y = st.number_input(f"Medido y ({tamanho}x{tamanho})", key=f"meas_y_{tamanho}", value=float(tamanho), step=0.1)
    dados_simetricos[f"{tamanho}x{tamanho}"] = {
        "expected": {"x": tamanho, "y": tamanho},
        "measured": {"x": medida_x, "y": medida_y}
    }
    st.markdown("---")

# Função para criar o gráfico do teste simétrico para um campo
def criar_grafico_campo_simetrico(expected, measured):
    """
    Cria um gráfico com o retângulo esperado (azul) e o retângulo medido (vermelho),
    além de uma área de tolerância (±2 mm, 0,2 cm) (verde tracejado).
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    escala = 0.1  # fator de conversão para visualização

    # Dimensões do campo esperado e medido
    width_exp = expected["x"] * escala
    height_exp = expected["y"] * escala
    width_meas = measured["x"] * escala
    height_meas = measured["y"] * escala

    # Desenha o retângulo esperado (azul) – centralizado
    ax.add_patch(plt.Rectangle((-width_exp/2, -height_exp/2), width_exp, height_exp,
                               fill=False, edgecolor="blue", lw=2, label="Padrão"))
    # Desenha o retângulo medido (vermelho) – centralizado
    ax.add_patch(plt.Rectangle((-width_meas/2, -height_meas/2), width_meas, height_meas,
                               fill=False, edgecolor="red", lw=2, label="Medido"))
    # Desenha a área de tolerância (verde tracejado)
    tol = 0.2 * escala  # 0,2 cm de tolerância convertidos para a escala
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

# Função para gerar o relatório PDF com os testes para cada campo
def gerar_relatorio_pdf(dados):
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

    # Para cada tamanho de campo, insere os dados e o gráfico correspondente
    for campo, info in dados.items():
        expected = info["expected"]
        measured = info["measured"]
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y, f"Campo {campo}")
        y -= 20
        c.setFont("Helvetica", 12)
        c.drawString(60, y, f"Padrão: x = {expected['x']} cm, y = {expected['y']} cm")
        c.drawString(300, y, f"Medido: x = {measured['x']} cm, y = {measured['y']} cm")
        # Verificação da tolerância (±0.2 cm)
        tol_valido = (expected['x'] - 0.2 <= measured['x'] <= expected['x'] + 0.2) and \
                     (expected['y'] - 0.2 <= measured['y'] <= expected['y'] + 0.2)
        c.setFillColor(colors.green if tol_valido else colors.red)
        c.drawString(500, y, f"{'Dentro' if tol_valido else 'Fora'} da tolerância (±2 mm)")
        c.setFillColor(colors.black)
        y -= 20

        # Insere o gráfico gerado para este campo
        grafico_buf = criar_grafico_campo_simetrico(expected, measured)
        img = ImageReader(grafico_buf)
        c.drawImage(img, 60, y - 200, width=200, height=200)
        y -= 220

        # Se o espaço vertical não for suficiente, cria uma nova página
        if y < 150:
            c.showPage()
            y = height - 100

    # Rodapé
    c.setFont("Helvetica", 10)
    c.drawString(60, 40, "Gerado por Streamlit - Testes de Tamanhos de Campo")
    c.drawString(width - 100, 40, "Página 1")
    c.save()
    buffer_pdf.seek(0)
    return buffer_pdf

# Botão para gerar o relatório PDF
if st.button("Gerar Relatório"):
    with st.spinner("Gerando relatório..."):
        pdf_buffer = gerar_relatorio_pdf(dados_simetricos)
        st.success("Relatório gerado com sucesso!")
        st.download_button(
            label="Baixar Relatório",
            data=pdf_buffer,
            file_name="Relatorio_Tamanhos_Campo.pdf",
            mime="application/pdf"
        )
