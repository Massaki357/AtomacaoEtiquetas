from flask import Blueprint, jsonify, request
from src.services.configService import ConfigService

config_bp = Blueprint('config', __name__)

@config_bp.route('/', methods=['GET'])
def get_config():
    try:
        config = ConfigService().load_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@config_bp.route('/update', methods=['POST'])
def update_config():
    try:
        new_config = request.json
        ConfigService().save_config(new_config)
        return jsonify({"message": "Config updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500