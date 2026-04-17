from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO
from pdf2image import convert_from_bytes
from datetime import datetime
import random
import sys
import os


def gerar_codigo():
    data = datetime.now()
    dia = f"{data.day:02d}"
    mes = f"{data.month:02d}"
    aleatorio = f"{random.randint(0,9)}{random.randint(0,9)}"
    return f"{dia}{aleatorio}{mes}"

def gerar_imagem_3col(name_product, price, path, noCode=False):
    # -------------------------------
    # Dimensões da etiqueta
    # -------------------------------

    print(name_product)

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    poppler_path = os.path.join(base_path, 'poppler', 'bin')

    code_product = gerar_codigo()
    if noCode == True:
        code_product = ""
    largura = 34 * mm
    altura = 22 * mm

    # Criar PDF em memória com o tamanho da etiqueta (NÃO A4)
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(largura, altura))

    x = 0 * mm
    y = 0 * mm

    # Desenhar retângulo da etiqueta
    c.rect(x, y, largura, altura)

    # -------------------------------
    # Nome do produto (30% da altura)
    # -------------------------------
    
    produto = f"{name_product}-{code_product}"
    if code_product == "":
        produto = name_product
    altura_nome = altura * 0.3
    margem = 1 * mm
    largura_max = largura - 2 * margem

    tamanho_fonte_base = 8
    c.setFont("Helvetica-Bold", tamanho_fonte_base)
    text_width = c.stringWidth(produto, "Helvetica-Bold", tamanho_fonte_base)

    if text_width <= largura_max:
        # Se couber em uma linha, expande proporcionalmente
        scale_x = largura_max / text_width
        c.saveState()
        c.translate(x + margem, y + altura - altura_nome + 3*mm)
        c.scale(scale_x, 1)
        c.drawString(0, 0, produto)
        c.restoreState()
    else:
        # Quebra em duas linhas se não couber
        palavras = produto.split()
        linha1 = ""
        linha2 = ""

        for palavra in palavras:
            largura_proxima = c.stringWidth(linha1 + " " + palavra, "Helvetica-Bold", tamanho_fonte_base)
            if largura_proxima <= largura_max:
                linha1 += (" " + palavra if linha1 else palavra)
            else:
                linha2 = " ".join(palavras[palavras.index(palavra):])
                break

        c.drawString(x + margem, y + altura - (altura_nome / 2) - 1 * mm, linha1)
        if linha2:
            c.drawString(x + margem, y + altura - (altura_nome / 2) - 4 * mm, linha2)

    # -------------------------------
    # Preço (70% da altura) + logo
    # -------------------------------
    preco = f"R${price:.2f}".replace('.', ',')
    c.setFont("Helvetica-Bold", 10)

    altura_preco = altura * 0.7
    largura_preco = largura * 0.7
    logo_width = largura * 0.2

    text_width = c.stringWidth(preco, "Helvetica-Bold", 10)
    scale_x = largura_preco / text_width
    scale_y = altura_preco / 10

    c.saveState()
    c.translate(x + margem, y + 2.5 *mm)
    c.scale(scale_x, scale_y)
    c.drawString(0, 0, preco)
    c.restoreState()

    # Logo
    logo_height = altura_preco * 0.7  # altura igual à do preço
    try:
        logo_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(logo_dir, "Logo.png")
        c.drawImage(
            logo_path,
            x + largura_preco + 2*mm,  # mesma posição X
            y + 2.5*mm,                # alinhado com o preço
            width=logo_width,          # mesma largura
            height=logo_height,        # esticada na vertical
            preserveAspectRatio=False  # permite deformar
        )
    except FileNotFoundError:
        return "Aviso: 'Logo.png' não encontrada. Será gerado sem a imagem.", 400

    # Finalizar PDF em memória
    c.save()
    pdf_buffer.seek(0)

    # -------------------------------
    # Converter PDF em PNG (sem bordas brancas)
    # -------------------------------
    images = convert_from_bytes(pdf_buffer.getvalue(), dpi=203, poppler_path=poppler_path)

    # Salvar a primeira (e única) página como PNG
    name_product = name_product.replace("/", ".")
    output_path = f"./etiquetas/{path}/{name_product}-{code_product}.png"
    images[0].save(output_path, "PNG")
    return f"{name_product}-{code_product}"

def gerar_imagem_2col(name_product, price, path, noCode=False):

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    poppler_path = os.path.join(base_path, 'poppler', 'bin')

    # -------------------------------
    # Dimensões da etiqueta
    # -------------------------------
    code_product = gerar_codigo()
    if noCode == True:
        code_product = ""
    largura = 50 * mm
    altura = 31 * mm

    # Criar PDF em memória com o tamanho da etiqueta (NÃO A4)
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(largura, altura))

    x = 0 * mm
    y = 0 * mm

    # Desenhar retângulo da etiqueta
    c.rect(x, y, largura, altura)

    # -------------------------------
    # Nome do produto (30% da altura)
    # -------------------------------
    produto = f"{name_product}-{code_product}"
    if code_product == "":
        produto = name_product
    altura_nome = altura * 0.3
    margem = 1 * mm
    largura_max = largura - 2 * margem

    tamanho_fonte_base = 8
    c.setFont("Helvetica-Bold", tamanho_fonte_base)
    text_width = c.stringWidth(produto, "Helvetica-Bold", tamanho_fonte_base)

    if text_width <= largura_max:
        # Se couber em uma linha, expande proporcionalmente
        scale_x = largura_max / text_width
        c.saveState()
        c.translate(x + margem, y + altura - altura_nome + 3*mm)
        c.scale(scale_x, 1)
        c.drawString(0, 0, produto)
        c.restoreState()
    else:
        # Quebra em duas linhas se não couber
        palavras = produto.split()
        linha1 = ""
        linha2 = ""

        for palavra in palavras:
            largura_proxima = c.stringWidth(linha1 + " " + palavra, "Helvetica-Bold", tamanho_fonte_base)
            if largura_proxima <= largura_max:
                linha1 += (" " + palavra if linha1 else palavra)
            else:
                linha2 = " ".join(palavras[palavras.index(palavra):])
                break

        c.drawString(x + margem, y + altura - (altura_nome / 2) - 1 * mm, linha1)
        if linha2:
            c.drawString(x + margem, y + altura - (altura_nome / 2) - 4 * mm, linha2)

    # -------------------------------
    # Preço (70% da altura) + logo
    # -------------------------------
    preco = f"R${price:.2f}".replace('.', ',')
    c.setFont("Helvetica-Bold", 10)

    altura_preco = altura * 0.7
    largura_preco = largura * 0.7
    logo_width = largura * 0.2

    text_width = c.stringWidth(preco, "Helvetica-Bold", 10)
    scale_x = largura_preco / text_width
    scale_y = altura_preco / 10

    c.saveState()
    c.translate(x + margem, y + 2.5 *mm)
    c.scale(scale_x, scale_y)
    c.drawString(0, 0, preco)
    c.restoreState()

    # Logo
    logo_height = altura_preco * 0.7  # altura igual à do preço
    try:
        logo_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(logo_dir, "Logo.png")
        c.drawImage(
            logo_path,
            x + largura_preco + 2*mm,  # mesma posição X
            y + 2.5*mm,                # alinhado com o preço
            width=logo_width,          # mesma largura
            height=logo_height,        # esticada na vertical
            preserveAspectRatio=False  # permite deformar
        )
    except FileNotFoundError:
        return "Aviso: 'Logo.png' não encontrada. Será gerado sem a imagem.", 400

    # Finalizar PDF em memória
    c.save()
    pdf_buffer.seek(0)

    # -------------------------------
    # Converter PDF em PNG (sem bordas brancas)
    # -------------------------------
    images = convert_from_bytes(pdf_buffer.getvalue(), dpi=203, poppler_path=poppler_path)

    # Salvar a primeira (e única) página como PNG
    name_product = name_product.replace("/", ".")
    output_path = f"./etiquetas/{path}/{name_product}-{code_product}.png"
    images[0].save(output_path, "PNG")
    return f"{name_product}-{code_product}"

def gerar_imagem_3linhas_planta(nome_planta, preco_un, preco_caixa, itens_caixa, path):

    print(nome_planta)

    # -------------------------------
    # Caminho do poppler
    # -------------------------------
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    poppler_path = os.path.join(base_path, 'poppler', 'bin')

    # -------------------------------
    # Dimensões da etiqueta
    # -------------------------------
    largura = 34 * mm
    altura = 22 * mm

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(largura, altura))

    x = 0
    y = 0

    # borda
    c.rect(x, y, largura, altura)

    margem = 0.7 * mm
    largura_util = largura - (2 * margem)

    # -------------------------------
    # Textos
    # -------------------------------
    nome = nome_planta.upper()
    texto_un = f"UN: R${preco_un:.2f}".replace(".", ",")
    texto_cx = f"CX/{itens_caixa}: R${preco_caixa:.2f}".replace(".", ",")

    # -------------------------------
    # NOME
    # -------------------------------
    fonte_nome = "Helvetica-Bold"
    tamanho_nome = 8

    c.setFont(fonte_nome, tamanho_nome)
    largura_nome = c.stringWidth(nome, fonte_nome, tamanho_nome)

    while largura_nome > largura_util and tamanho_nome > 5:
        tamanho_nome -= 0.5
        largura_nome = c.stringWidth(nome, fonte_nome, tamanho_nome)

    x_nome = x + (largura - largura_nome) / 2
    y_nome = y + altura - 3.8 * mm   # sobe o nome e reduz espaço vazio em cima
    c.setFont(fonte_nome, tamanho_nome)
    c.drawString(x_nome, y_nome, nome)

    # -------------------------------
    # VALORES
    # -------------------------------
    fonte_preco = "Helvetica-Bold"
    tamanho_base_preco = 8.5

    c.setFont(fonte_preco, tamanho_base_preco)

    # área horizontal útil
    largura_preco = largura_util

    # aqui controla o "esticamento" vertical
    escala_vertical = 2.15

    # aqui controla a altura base visual dos números
    altura_visual_preco = 4.6 * mm

    # posições Y dos preços
    # subi os valores e aumentei a separação entre eles
    y_un = y + 9.6 * mm
    y_cx = y + 1.8 * mm

    # -------- UN --------
    largura_texto_un = c.stringWidth(texto_un, fonte_preco, tamanho_base_preco)
    scale_x_un = largura_preco / largura_texto_un
    scale_y_un = (altura_visual_preco / tamanho_base_preco) * escala_vertical

    if scale_x_un > 1.95:
        scale_x_un = 1.95

    c.saveState()
    c.translate(x + margem, y_un)
    c.scale(scale_x_un, scale_y_un)
    c.drawString(0, 0, texto_un)
    c.restoreState()

    # -------- CX --------
    largura_texto_cx = c.stringWidth(texto_cx, fonte_preco, tamanho_base_preco)
    scale_x_cx = largura_preco / largura_texto_cx
    scale_y_cx = (altura_visual_preco / tamanho_base_preco) * escala_vertical

    if scale_x_cx > 1.95:
        scale_x_cx = 1.95

    c.saveState()
    c.translate(x + margem, y_cx)
    c.scale(scale_x_cx, scale_y_cx)
    c.drawString(0, 0, texto_cx)
    c.restoreState()

    # -------------------------------
    # Finaliza PDF
    # -------------------------------
    c.save()
    pdf_buffer.seek(0)

    # -------------------------------
    # Converte para PNG
    # -------------------------------
    images = convert_from_bytes(
        pdf_buffer.getvalue(),
        dpi=203,
        poppler_path=poppler_path
    )

    nome_arquivo = nome_planta.replace("/", ".").upper()

    output_dir = f"./etiquetas/{path}"
    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/{nome_arquivo}.png"
    images[0].save(output_path, "PNG")

    return f"{nome_arquivo}.png"

def gerar_imagem_2col_planta(nome_planta, preco_un, preco_caixa, itens_caixa, path):

    print(nome_planta)

    # -------------------------------
    # Caminho do poppler
    # -------------------------------
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    poppler_path = os.path.join(base_path, 'poppler', 'bin')

    # -------------------------------
    # Dimensões da etiqueta 2 colunas
    # -------------------------------
    largura = 50 * mm
    altura = 31 * mm

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(largura, altura))

    x = 0
    y = 0

    # borda
    c.rect(x, y, largura, altura)

    margem = 0.7 * mm
    largura_util = largura - (2 * margem)

    # -------------------------------
    # Textos
    # -------------------------------
    nome = nome_planta.upper()
    texto_un = f"UN: R${preco_un:.2f}".replace(".", ",")
    texto_cx = f"CX/{itens_caixa}: R${preco_caixa:.2f}".replace(".", ",")

    # -------------------------------
    # NOME
    # -------------------------------
    fonte_nome = "Helvetica-Bold"
    tamanho_nome = 11

    c.setFont(fonte_nome, tamanho_nome)
    largura_nome = c.stringWidth(nome, fonte_nome, tamanho_nome)

    while largura_nome > largura_util and tamanho_nome > 6:
        tamanho_nome -= 0.5
        largura_nome = c.stringWidth(nome, fonte_nome, tamanho_nome)

    x_nome = x + (largura - largura_nome) / 2
    y_nome = y + altura - 4.5 * mm
    c.setFont(fonte_nome, tamanho_nome)
    c.drawString(x_nome, y_nome, nome)

    # -------------------------------
    # VALORES
    # -------------------------------
    fonte_preco = "Helvetica-Bold"
    tamanho_base_preco = 11

    c.setFont(fonte_preco, tamanho_base_preco)

    largura_preco = largura_util

    # controla o alongamento vertical
    escala_vertical = 2.2

    # controla a altura visual base
    altura_visual_preco = 6.0 * mm

    # posições verticais
    y_un = y + 13.5 * mm
    y_cx = y + 3.0 * mm

    # -------- UN --------
    largura_texto_un = c.stringWidth(texto_un, fonte_preco, tamanho_base_preco)
    scale_x_un = largura_preco / largura_texto_un
    scale_y_un = (altura_visual_preco / tamanho_base_preco) * escala_vertical

    if scale_x_un > 2.0:
        scale_x_un = 2.0

    c.saveState()
    c.translate(x + margem, y_un)
    c.scale(scale_x_un, scale_y_un)
    c.drawString(0, 0, texto_un)
    c.restoreState()

    # -------- CX --------
    largura_texto_cx = c.stringWidth(texto_cx, fonte_preco, tamanho_base_preco)
    scale_x_cx = largura_preco / largura_texto_cx
    scale_y_cx = (altura_visual_preco / tamanho_base_preco) * escala_vertical

    if scale_x_cx > 2.0:
        scale_x_cx = 2.0

    c.saveState()
    c.translate(x + margem, y_cx)
    c.scale(scale_x_cx, scale_y_cx)
    c.drawString(0, 0, texto_cx)
    c.restoreState()

    # -------------------------------
    # Finaliza PDF
    # -------------------------------
    c.save()
    pdf_buffer.seek(0)

    # -------------------------------
    # Converte para PNG
    # -------------------------------
    images = convert_from_bytes(
        pdf_buffer.getvalue(),
        dpi=203,
        poppler_path=poppler_path
    )

    nome_arquivo = nome_planta.replace("/", ".").upper()

    output_dir = f"./etiquetas/{path}"
    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/{nome_arquivo}.png"
    images[0].save(output_path, "PNG")

    return f"{nome_arquivo}.png"