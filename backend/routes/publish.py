from flask import Blueprint, jsonify, request

from ..services.content_service import ContentService

bp = Blueprint('publish', __name__)
service = ContentService()


@bp.post('/api/publish/simulate')
def simulate_publish():
    data = request.get_json(force=True)
    draft_id = data.get('platform_draft_id')
    if not draft_id:
        return jsonify({'code': 400, 'msg': '缺少平台草稿ID'}), 400
    task = service.simulate_publish(draft_id)
    if not task:
        return jsonify({'code': 404, 'msg': '平台草稿不存在'}), 404
    return jsonify({'code': 200, 'data': task})


@bp.post('/api/publish/simulate-batch')
def simulate_publish_batch():
    data = request.get_json(force=True)
    draft_ids = data.get('platform_draft_ids') or []
    if not draft_ids:
        return jsonify({'code': 400, 'msg': '请选择要发布的平台草稿'}), 400
    return jsonify({'code': 200, 'data': service.simulate_publish_batch(draft_ids)})


@bp.get('/api/publish/tasks')
def list_tasks():
    return jsonify({'code': 200, 'data': service.tasks.list()})
