import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime
import matplotlib.pyplot as plt

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
        margin: 2px !important;
        padding: 0px !important;
        width: 60px !important;
    }
    .stNumberInput > div {
        margin: 0px !important;
        padding: 0px !important;
    }
    /* Ajuste das colunas internas (X e Y) */
    [class*="stHorizontal"] > div {
        max-width: 200px !important;
        margin-right: 2px !important;
        margin-left: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Função para criar gráficos e retornar imagem em memória (BytesIO)
def criar_grafico_campo(padrao, medido, tipo, tamanho=None):
    fig, ax = plt.subplots(figsize=(5, 5))
    escala = 0.1  # conversão de cm para uma escala ajustada para plotagem
    if tipo == "simetrico":
        x_padrao = y_padrao = tamanho * escala
        x_medido = medido["x"] * escala
        y_medido = medido["y"] * escala
        ax.set_title(f"Campo Simétrico {tamanho}x{tamanho} cm")
    else:
        x_padrao = (padrao["x2"] - padrao["x1"]) * escala
        y_padrao = (padrao["y2"] - padrao["y1"]) * escala
        x_medido = (medido["x2"] - medido["x1"]) * escala
        y_medido = (medido["y2"] - medido["y1"]) * escala
        ax.set_title("Campo Assimétrico")

    # Desenha o campo padrão (azul) e medido (vermelho)
    ax.add_patch(plt.Rectangle((-x_padrao/2, -y_padrao/2), x_padrao, y_padrao, fill=False, color="blue", label="Padrão"))
    ax.add_patch(plt.Rectangle((-x_medido/2, -y_medido/2), x_medido, y_medido, fill=False, color="red", label="Medido"))
    
    # Adiciona a tolerância (±2 mm, considerando escala)
    tolerancia = 0.2 * escala  # 2mm = 0.2 cm
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
    
    # Salva a figura em um buffer de memória
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

# Função para gerar o PDF do relatório
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

    # Seção dos Testes Simétricos
    if dados_simetricos:
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y, "Testes Simétricos")
        y -= 20
        tamanhos = [5, 10, 15, 20, 25]
        for tamanho in tamanhos:
            medidas = dados_simetricos[f"{tamanho}x{tamanho}"]
            x_medido = medidas["x"]
            y_medido = medidas["y"]
            c.setFont("Helvetica", 12)
            c.drawString(60, y, f"Campo {tamanho}x{tamanho} cm: X = {x_medido} cm, Y = {y_medido} cm")
            # Validação de tolerância
            dentro_tolerancia = (tamanho - 0.2) <= x_medido <= (tamanho + 0.2) and (tamanho - 0.2) <= y_medido <= (tamanho + 0.2)
            c.setFillColor(colors.green if dentro_tolerancia else colors.red)
            c.drawString(300, y, f"{'Dentro' if dentro_tolerancia else 'Fora'} da tolerância (±2 mm)")
            c.setFillColor(colors.black)
            # Gera o gráfico e insere no PDF
            grafico_buf = criar_grafico_campo(None, {"x": x_medido, "y": y_medido}, "simetrico", tamanho)
            img = ImageReader(grafico_buf)
            c.drawImage(img, 60, y - 150, width=200, height=200)
            y -= 220

    # Seção dos Testes Assimétricos
    if dados_assimetricos:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y, "Testes Assimétricos")
        y -= 20
        c.setFont("Helvetica", 12)
        padrao = dados_assimetricos["padrao"]
        medido = dados_assimetricos["medido"]
        c.drawString(60, y, f"Padrão: X1={padrao['x1']}, X2={padrao['x2']}, Y1={padrao['y1']}, Y2={padrao['y2']} cm")
        y -= 20
        c.drawString(60, y, f"Medido: X1={medido['x1']}, X2={medido['x2']}, Y1={medido['y1']}, Y2={medido['y2']} cm")
        y -= 20
        # Validação da tolerância para cada dimensão
        tolerancia = 0.2
        validacoes = [
            (padrao['x1'] - tolerancia) <= medido['x1'] <= (padrao['x1'] + tolerancia),
            (padrao['x2'] - tolerancia) <= medido['x2'] <= (padrao['x2'] + tolerancia),
            (padrao['y1'] - tolerancia) <= medido['y1'] <= (padrao['y1'] + tolerancia),
            (padrao['y2'] - tolerancia) <= medido['y2'] <= (padrao['y2'] + tolerancia)
        ]
        c.setFillColor(colors.green if all(validacoes) else colors.red)
        c.drawString(300, y+20, f"{'Dentro' if all(validacoes) else 'Fora'} da tolerância (±2 mm)")
        c.setFillColor(colors.black)
        # Gera o gráfico para campo assimétrico
        grafico_buf = criar_grafico_campo(padrao, medido, "assimetrico")
        img = ImageReader(grafico_buf)
        c.drawImage(img, 60, y - 150, width=200, height=200)

    # Rodapé
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(60, 40, "Gerado por Streamlit - Testes de Tamanhos de Campo")
    c.drawString(width - 100, 40, "Página 1")
    c.save()
    buffer_pdf.seek(0)
    return buffer_pdf

# Interface do Streamlit
st.markdown('<div style="font-size: 36px; font-weight: bold; color: #1e90ff; text-align: center; margin-bottom: 20px;">📏 Testes de Tamanhos de Campo</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size: 18px; color: #1e90ff; text-align: center; margin-bottom: 40px;">Insira os valores medidos para gerar um relatório com representações visuais</div>', unsafe_allow_html=True)

# Divisão em três colunas: simétricos, espaço e assimétricos
col1, spacer, col2 = st.columns([2, 1, 2])

dados_simetricos = {}
dados_assimetricos = {}

# Entrada dos Testes Simétricos
with col1:
    st.markdown('<div style="font-size: 24px; color: #800080; font-weight: bold; margin-top: 20px; margin-bottom: 10px;">Campos Simétricos</div>', unsafe_allow_html=True)
    for tamanho in [5, 10, 15, 20, 25]:
        st.write(f"Campo {tamanho}x{tamanho} cm")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            x = st.number_input("X", min_value=0.0, max_value=30.0, value=float(tamanho), step=0.1, key=f"x_{tamanho}")
        with subcol2:
            y = st.number_input("Y", min_value=0.0, max_value=30.0, value=float(tamanho), step=0.1, key=f"y_{tamanho}")
        dados_simetricos[f"{tamanho}x{tamanho}"] = {"x": x, "y": y}
        st.markdown("<hr style='border: 1px solid #00ff00; margin: 5px 0;' />", unsafe_allow_html=True)

# Espaço entre as colunas
with spacer:
    st.write("")

# Entrada dos Testes Assimétricos
with col2:
    st.markdown('<div style="font-size: 24px; color: #800080; font-weight: bold; margin-top: 20px; margin-bottom: 10px;">Campo Assimétrico</div>', unsafe_allow_html=True)
    
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

# Botão para gerar o relatório
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
