from flask import Blueprint, jsonify

from ..adapters.registry import list_platforms
from ..config import DB_PATH

bp = Blueprint('health', __name__)


@bp.get('/api/health')
def health():
    return jsonify({
        'code': 200,
        'data': {
            'status': 'ok',
            'database': str(DB_PATH),
            'platforms': list_platforms(),
        },
    })
