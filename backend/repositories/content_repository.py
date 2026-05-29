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
                '''INSERT INTO contents (title, summary, body, cover_image, content_type, tags)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    data['title'],
                    data.get('summary', ''),
                    data['body'],
                    data.get('cover_image', ''),
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
                   SET title = ?, summary = ?, body = ?, cover_image = ?, content_type = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (
                    merged['title'],
                    merged.get('summary', ''),
                    merged['body'],
                    merged.get('cover_image', ''),
                    merged.get('content_type', 'article'),
                    tags,
                    content_id,
                ),
            )
            conn.commit()
        return self.get(content_id)

    def _decode(self, row):
        if not row:
            return None
        row['tags'] = json.loads(row.get('tags') or '[]')
        return row
