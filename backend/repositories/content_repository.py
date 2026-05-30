import json

from ..db import get_connection, row_to_dict


class ContentRepository:
    def list(self):
        with get_connection() as conn:
            rows = conn.execute('SELECT * FROM contents ORDER BY updated_at DESC, id DESC').fetchall()
            return [self._decode(row_to_dict(row)) for row in rows]

    def get(self, content_id):
        with get_connection() as conn:
            row = conn.execute('SELECT * FROM contents WHERE id = ?', (content_id,)).fetchone()
            return self._decode(row_to_dict(row))

    def create(self, data):
        tags = json.dumps(data.get('tags', []), ensure_ascii=False)
        with get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO contents (title, summary, body, cover_image, video_path, content_type, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    data['title'],
                    data.get('summary', ''),
                    data['body'],
                    data.get('cover_image', ''),
                    data.get('video_path', ''),
                    data.get('content_type', 'article'),
                    tags,
                ),
            )
            conn.commit()
            return self.get(cursor.lastrowid)

    def update(self, content_id, data):
        current = self.get(content_id)
        if not current:
            return None
        merged = {**current, **data}
        tags = json.dumps(merged.get('tags', []), ensure_ascii=False)
        with get_connection() as conn:
            conn.execute(
                '''UPDATE contents
                   SET title = ?, summary = ?, body = ?, cover_image = ?, video_path = ?, content_type = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (
                    merged['title'],
                    merged.get('summary', ''),
                    merged['body'],
                    merged.get('cover_image', ''),
                    merged.get('video_path', ''),
                    merged.get('content_type', 'article'),
                    tags,
                    content_id,
                ),
            )
            conn.commit()
        return self.get(content_id)

    def delete(self, content_id):
        with get_connection() as conn:
            content = conn.execute('SELECT id FROM contents WHERE id = ?', (content_id,)).fetchone()
            if not content:
                return False

            conn.execute(
                '''DELETE FROM publish_tasks
                   WHERE platform_draft_id IN (
                       SELECT id FROM platform_drafts WHERE content_id = ?
                   )''',
                (content_id,),
            )
            conn.execute('DELETE FROM platform_drafts WHERE content_id = ?', (content_id,))
            conn.execute('DELETE FROM contents WHERE id = ?', (content_id,))
            conn.commit()
            return True

    def _decode(self, row):
        if not row:
            return None
        row['tags'] = json.loads(row.get('tags') or '[]')
        return row
