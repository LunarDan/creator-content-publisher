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


@bp.post('/api/publish/zhihu/browser')
def publish_zhihu_with_browser():
    data = request.get_json(force=True)
    draft_id = data.get('platform_draft_id')
    if not draft_id:
        return jsonify({'code': 400, 'msg': '缺少平台草稿ID'}), 400

    auto_publish = False
    result, error = service.publish_zhihu_with_browser(draft_id, auto_publish=auto_publish)
    if error:
        status = 404 if error == '平台草稿不存在' else 400
        return jsonify({'code': status, 'msg': error, 'data': result}), status
    return jsonify({'code': 200, 'data': result})


@bp.post('/api/publish/bilibili/browser')
def publish_bilibili_with_browser():
    data = request.get_json(force=True)
    draft_id = data.get('platform_draft_id')
    if not draft_id:
        return jsonify({'code': 400, 'msg': '缺少平台草稿ID'}), 400

    auto_publish = data.get('auto_publish', True)
    result, error = service.publish_bilibili_with_browser(draft_id, auto_publish=auto_publish)
    if error:
        status = 404 if error == '平台草稿不存在' else 400
        return jsonify({'code': status, 'msg': error, 'data': result}), status
    return jsonify({'code': 200, 'data': result})


@bp.post('/api/publish/douyin/browser')
def publish_douyin_with_browser():
    data = request.get_json(force=True)
    draft_id = data.get('platform_draft_id')
    if not draft_id:
        return jsonify({'code': 400, 'msg': '缺少平台草稿ID'}), 400

    auto_publish = data.get('auto_publish', True)
    result, error = service.publish_douyin_with_browser(draft_id, auto_publish=auto_publish)
    if error:
        status = 404 if error == '平台草稿不存在' else 400
        return jsonify({'code': status, 'msg': error, 'data': result}), status
    return jsonify({'code': 200, 'data': result})


@bp.post('/api/publish/kuaishou/browser')
def publish_kuaishou_with_browser():
    data = request.get_json(force=True)
    draft_id = data.get('platform_draft_id')
    if not draft_id:
        return jsonify({'code': 400, 'msg': '缺少平台草稿ID'}), 400

    result, error = service.publish_kuaishou_with_browser(draft_id, auto_publish=False)
    if error:
        status = 404 if error == '平台草稿不存在' else 400
        return jsonify({'code': status, 'msg': error, 'data': result}), status
    return jsonify({'code': 200, 'data': result})


@bp.post('/api/publish/wechat/draft')
def publish_wechat_draft():
    data = request.get_json(force=True)
    draft_id = data.get('platform_draft_id')
    if not draft_id:
        return jsonify({'code': 400, 'msg': '缺少平台草稿ID'}), 400

    result, error = service.publish_wechat_draft(draft_id)
    if error:
        status = 404 if error == '平台草稿不存在' else 400
        return jsonify({'code': status, 'msg': error, 'data': result}), status
    return jsonify({'code': 200, 'data': result})


@bp.get('/api/publish/wechat/config')
def get_wechat_publish_config():
    return jsonify({'code': 200, 'data': service.get_wechat_publish_config()})


@bp.get('/api/publish/wechat/token-check')
def check_wechat_token():
    result, error = service.check_wechat_token()
    if error:
        return jsonify({'code': 400, 'msg': error}), 400
    return jsonify({'code': 200, 'data': result})


@bp.post('/api/publish/tasks/<task_id>/complete-manual')
def complete_manual_publish(task_id):
    data = request.get_json(force=True)
    task, error = service.complete_manual_publish(task_id, data.get('publish_url', '').strip())
    if error:
        status = 404 if error == '发布任务不存在' else 400
        return jsonify({'code': status, 'msg': error}), status
    return jsonify({'code': 200, 'data': task})


@bp.get('/api/publish/tasks')
def list_tasks():
    return jsonify({'code': 200, 'data': service.tasks.list()})
