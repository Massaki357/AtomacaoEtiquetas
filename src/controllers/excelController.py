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
    
@excel_bp.route('/togheter', methods=['POST'])
def join_excel():
    try:
        service = ExcelService()
        data_body = request.get_json()
        excel1 = data_body.get('excel1')
        excel2 = data_body.get('excel2')
        if not excel1 or not excel2:
            return jsonify({'error': 'Dois arquivos Excel são necessários.'}), 400
        resultado = service.join_excel(excel1, excel2, './resultado-tabelas')
        return jsonify({'message': 'Sucesso em juntar as tabelas', 'result': resultado}), 200
    except Exception as e:
        print(f"Erro no serviço de teste: {e}")
        return jsonify({'error': str(e)}), 500
