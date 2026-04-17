import pandas as pd
import math
from imprimir import imprimir_imagem, imprimir_2cols
from gerarImagem import gerar_imagem_3col, gerar_imagem_2col
import time
from datetime import datetime
import os
from flask import Flask, request
from flask_cors import CORS
from src.controllers.printerController import printer_bp
from src.controllers.excelController import excel_bp
from src.controllers.configController import config_bp
from threading import Thread, Event
import subprocess

pause_event = Event()
pause_event.set()  # Inicia como não pausado

stop_event = Event()  # Evento para sinalizar parada
printing_status = "idle"  # idle | printing | paused | cancelled

def processar_impressao(df, tipo, sheet, printer, noCode, double):
    global printing_status

    printing_status = "printing"
    stop_event.clear()
    pause_event.set()

    try:
        date = datetime.now()
        day = f"{date.day:02d}"
        month = f"{date.month:02d}"
        year = f"{date.year:04d}"

        if tipo == "3col":
            path = f"{year}/3 col/{day}-{month}/"
            divisor = 3
        else:
            path = f"{year}/2 col/{day}-{month}/"
            divisor = 2

        for index, row in df.iterrows():

            # 🔴 CANCELAMENTO
            if stop_event.is_set():
                printing_status = "cancelled"
                print("Impressão cancelada.")
                return

            # ⏸ PAUSA
            while not pause_event.is_set():
                printing_status = "paused"
                if stop_event.is_set():
                    printing_status = "cancelled"
                    print("Impressão cancelada.")
                    return
                time.sleep(0.3)

            printing_status = "printing"

            nome = row['Nome'].upper()
            rawPrice = str(row['Valor']).replace(',', '.').replace('R$', '')

            if rawPrice == '' or rawPrice.lower() in ('nan', 'none'):
                continue

            try:
                preco = float(rawPrice)
            except ValueError:
                continue

            quantidade = math.ceil(int(row['Quantidade']) / divisor)

            if double:
                quantidade *= 2

            if 'Abreviação' in df.columns:
                if not pd.isna(row['Abreviação']) and str(row['Abreviação']).strip() != '':
                    nome = str(row['Abreviação']).upper()

            if quantidade < divisor:
                quantidade = divisor

            os.makedirs(f"./etiquetas/{path}", exist_ok=True)

            # 🔹 Gerar imagem
            if tipo == "3col":
                name_img = gerar_imagem_3col(nome, preco, path, noCode)
            else:
                name_img = gerar_imagem_2col(nome, preco, path, noCode)

            # 🔹 Impressão
            for i in range(quantidade):

                if stop_event.is_set():
                    printing_status = "cancelled"
                    print("Impressão cancelada.")
                    return

                while not pause_event.is_set():
                    printing_status = "paused"
                    if stop_event.is_set():
                        printing_status = "cancelled"
                        return
                    time.sleep(0.3)

                printing_status = "printing"

                if tipo == "3col":
                    imprimir_imagem(name_img, path, printer)
                else:
                    imprimir_2cols(name_img, path, printer)

            calc_sleep = (quantidade * 1.3) + 5
            time.sleep(calc_sleep)

        printing_status = "idle"
        print("Processamento finalizado com sucesso.")

    except Exception as e:
        printing_status = "idle"
        print(f"Erro no processamento: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def imprimir_excel():

    if 'excel' not in request.files:
        return "Nenhum arquivo Excel enviado", 400

    arquivo = request.files['excel']
    sheet = request.form.get('sheet')
    printer = request.form.get('printer')
    noCode = bool(request.form.get('code'))
    double = bool(request.form.get('double'))

    if not arquivo.filename.endswith('.xlsx'):
        return "Arquivo enviado não é um arquivo Excel válido", 400

    if not sheet:
        return "Você precisa selecionar uma Planilha", 400

    df = pd.read_excel(arquivo, sheet_name=sheet)

    Thread(
        target=processar_impressao,
        args=(df, "3col", sheet, printer, noCode, double)
    ).start()

    return "Impressão iniciada!", 200

@app.route('/big', methods=['POST'])
def imprimir_big():

    if 'excel' not in request.files:
        return "Nenhum arquivo Excel enviado", 400

    arquivo = request.files['excel']
    sheet = request.form.get('sheet')
    printer = request.form.get('printer')
    noCode = bool(request.form.get('code'))
    double = bool(request.form.get('double'))

    if not arquivo.filename.endswith('.xlsx'):
        return "Arquivo enviado não é um arquivo Excel válido", 400

    if not sheet:
        return "Você precisa selecionar uma Planilha", 400

    df = pd.read_excel(arquivo, sheet_name=sheet)

    Thread(
        target=processar_impressao,
        args=(df, "2col", sheet, printer, noCode, double)
    ).start()

    return "Impressão iniciada!", 200

@app.route('/one', methods=['POST'])
def imprimir_one():

    date = datetime.now()
    day = f"{date.day:02d}"
    month = f"{date.month:02d}"
    year = f"{date.year:04d}"
    path2col = f"{year}/2 col/{day}-{month}/"
    path3col = f"{year}/3 col/{day}-{month}/"

    data = request.get_json()
    nome = data.get('name').upper()
    printer = data.get('printer')
    noCode = bool(data.get('code'))

    rawPrice = str(data.get('price').replace(',', '.').replace('R$', ''))
    preco = float(rawPrice)
    col = data.get('col')

    if col == '2':
        quantidade = math.ceil(int(data.get('qtd')) / 2)  # arredonda para cima
        os.makedirs(f"./etiquetas/{path2col}", exist_ok=True)  # cria o diretório se não existir
        name_img = gerar_imagem_2col(nome, preco, path2col, noCode)
        
        for i in range(quantidade):
            imprimir_2cols(name_img, path2col, printer)
            
    elif col == '3':
        quantidade = math.ceil(int(data.get('qtd')) / 3)  # arredonda para cima
        os.makedirs(f"./etiquetas/{path3col}", exist_ok=True)  # cria o diretório se não existir
        name_img = gerar_imagem_3col(nome, preco, path3col, noCode)
        
        for i in range(quantidade):
            imprimir_imagem(name_img, path3col, printer)
    
    return "Impressão concluída com sucesso!", 200

@app.route('/pause', methods=['GET'])
def pause():
    try:
        pause_event.clear()
        return "Impressão pausada"
    except Exception as e:
        return f"Erro ao pausar a impressão: {e}", 500

@app.route('/play', methods=['GET'])
def play():
    pause_event.set()
    return "Impressão retomada"

@app.route('/cancel', methods=['GET'])
def cancel():
    stop_event.set()
    pause_event.set()
    return "Impressão cancelada"

app.register_blueprint(printer_bp, url_prefix='/printers')
app.register_blueprint(excel_bp, url_prefix='/excel')
app.register_blueprint(config_bp, url_prefix='/config')


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
