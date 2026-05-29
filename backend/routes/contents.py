from flask import Blueprint, jsonify, request

from ..services.content_service import ContentService

bp = Blueprint('contents', __name__)
service = ContentService()


@bp.get('/api/contents')
def list_contents():
    return jsonify({'code': 200, 'data': service.list_contents()})


@bp.post('/api/contents')
def create_content():
    data = request.get_json(force=True)
    if not data.get('title') or not data.get('body'):
        return jsonify({'code': 400, 'msg': '标题和正文不能为空'}), 400
    return jsonify({'code': 200, 'data': service.create_content(data)})


@bp.get('/api/contents/<int:content_id>')
def get_content(content_id):
    content = service.get_content(content_id)
    if not content:
        return jsonify({'code': 404, 'msg': '内容不存在'}), 404
    return jsonify({'code': 200, 'data': content})


@bp.put('/api/contents/<int:content_id>')
def update_content(content_id):
    content = service.update_content(content_id, request.get_json(force=True))
    if not content:
        return jsonify({'code': 404, 'msg': '内容不存在'}), 404
    return jsonify({'code': 200, 'data': content})


@bp.delete('/api/contents/<int:content_id>')
def delete_content(content_id):
    deleted = service.delete_content(content_id)
    if not deleted:
        return jsonify({'code': 404, 'msg': '内容不存在'}), 404
    return jsonify({'code': 200, 'data': True})


@bp.post('/api/contents/<int:content_id>/adapt')
def adapt_content(content_id):
    data = request.get_json(silent=True) or {}
    drafts = service.adapt_content(content_id, data.get('platforms', []))
    if drafts is None:
        return jsonify({'code': 404, 'msg': '内容不存在'}), 404
    return jsonify({'code': 200, 'data': drafts})


@bp.get('/api/contents/<int:content_id>/platform-drafts')
def list_platform_drafts(content_id):
    return jsonify({'code': 200, 'data': service.list_platform_drafts(content_id)})
