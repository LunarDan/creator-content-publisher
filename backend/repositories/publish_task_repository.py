import uuid

from ..db import get_connection, row_to_dict


class PublishTaskRepository:
    def list(self):
        with get_connection() as conn:
            rows = conn.execute('SELECT * FROM publish_tasks ORDER BY created_at DESC').fetchall()
            return [row_to_dict(row) for row in rows]

    def create_simulated(self, draft):
        task_id = str(uuid.uuid4())
        with get_connection() as conn:
            conn.execute(
                '''INSERT INTO publish_tasks
                   (id, content_id, platform_draft_id, platform, mode, status, title, publish_url, started_at, finished_at)
                   VALUES (?, ?, ?, ?, 'simulate', 'simulated', ?, '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)''',
                (task_id, draft['content_id'], draft['id'], draft['platform'], draft['title']),
            )
            conn.commit()
        return self.get(task_id)

    def create_browser(self, draft):
        task_id = str(uuid.uuid4())
        with get_connection() as conn:
            conn.execute(
                '''INSERT INTO publish_tasks
                   (id, content_id, platform_draft_id, platform, mode, status, title, publish_url)
                   VALUES (?, ?, ?, ?, 'browser', 'pending', ?, '')''',
                (task_id, draft['content_id'], draft['id'], draft['platform'], draft['title']),
            )
            conn.commit()
        return self.get(task_id)

    def mark_running(self, task_id):
        with get_connection() as conn:
            conn.execute(
                '''UPDATE publish_tasks
                   SET status = 'running', started_at = CURRENT_TIMESTAMP, error_message = ''
                   WHERE id = ?''',
                (task_id,),
            )
            conn.commit()
        return self.get(task_id)

    def mark_manual_pending(self, task_id, message=''):
        with get_connection() as conn:
            conn.execute(
                '''UPDATE publish_tasks
                   SET status = 'manual_pending', error_message = ?
                   WHERE id = ?''',
                (message, task_id),
            )
            conn.commit()
        return self.get(task_id)

    def mark_success(self, task_id, publish_url=''):
        with get_connection() as conn:
            conn.execute(
                '''UPDATE publish_tasks
                   SET status = 'success', publish_url = ?, error_message = '', finished_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (publish_url, task_id),
            )
            conn.commit()
        return self.get(task_id)

    def mark_failed(self, task_id, error_message):
        with get_connection() as conn:
            conn.execute(
                '''UPDATE publish_tasks
                   SET status = 'failed', error_message = ?, finished_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (error_message, task_id),
            )
            conn.commit()
        return self.get(task_id)

    def get(self, task_id):
        with get_connection() as conn:
            row = conn.execute('SELECT * FROM publish_tasks WHERE id = ?', (task_id,)).fetchone()
            return row_to_dict(row)
