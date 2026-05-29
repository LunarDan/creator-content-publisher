from flask import Blueprint, jsonify, request

from ..adapters.registry import list_platforms

bp = Blueprint('platforms', __name__)


@bp.get('/api/platforms')
def platforms():
    return jsonify({'code': 200, 'data': list_platforms()})
