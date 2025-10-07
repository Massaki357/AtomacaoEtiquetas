from flask import Blueprint, jsonify, request
from src.services.excelService import ExcelService

excel_bp = Blueprint('excel', __name__)

@excel_bp.route('/comparar', methods=['POST'])
def comparar_tabelas():
    try:
        #Chamar o serviço para comparar as tabelas e passar 2 parametros com o caminho dos arquivos
        if 'excel1' not in request.files or 'excel2' not in request.files:
            return jsonify({'error': 'Dois arquivos Excel são necessários.'}), 400
        
        service = ExcelService()
        resultado = service.comparar_tabelas(request.files['excel1'], request.files['excel2'])
        return jsonify({'message': 'Comparação concluída com sucesso.', 'diferenças': resultado.to_dict(orient='records')}), 200
    except Exception as e:
        print(f"Erro ao comparar tabelas: {e}")
        return jsonify({'error': str(e)}), 500
    
@excel_bp.route('/together', methods=['POST'])
def join_excel():
    try:
        service = ExcelService()
        excel1 = request.files['pedido']
        excel2 = request.files['venda']
        code = bool(request.form.get('withCode'))
        print(code)
        if not excel1 or not excel2:
            return jsonify({'error': 'Dois arquivos Excel são necessários.'}), 400
        resultado = service.two_excel(excel1, excel2, './resultado-tabelas', code)
        return jsonify({'message': 'Sucesso em juntar as tabelas', 'result': resultado}), 200
    except Exception as e:
        print(f"Erro no serviço de teste: {e}")
        return jsonify({'error': str(e)}), 500
