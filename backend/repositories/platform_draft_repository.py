import json

from ..db import get_connection, row_to_dict


class PlatformDraftRepository:
    def list_by_content(self, content_id):
        with get_connection() as conn:
            rows = conn.execute('SELECT * FROM platform_drafts WHERE content_id = ? ORDER BY id ASC', (content_id,)).fetchall()
            return [self._decode(row_to_dict(row)) for row in rows]

    def get(self, draft_id):
        with get_connection() as conn:
            row = conn.execute('SELECT * FROM platform_drafts WHERE id = ?', (draft_id,)).fetchone()
            return self._decode(row_to_dict(row))

    def upsert(self, content_id, draft):
        tags = json.dumps(draft.get('tags', []), ensure_ascii=False)
        extra_config = json.dumps(draft.get('extra_config', {}), ensure_ascii=False)
        warnings = json.dumps(draft.get('validation_warnings', []), ensure_ascii=False)
        with get_connection() as conn:
            existing = conn.execute(
                'SELECT id FROM platform_drafts WHERE content_id = ? AND platform = ?',
                (content_id, draft['platform']),
            ).fetchone()
            if existing:
                conn.execute(
                    '''UPDATE platform_drafts
                       SET title = ?, body = ?, summary = ?, tags = ?, cover_image = ?, extra_config = ?, validation_warnings = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?''',
                    (draft['title'], draft['body'], draft.get('summary', ''), tags, draft.get('cover_image', ''), extra_config, warnings, existing['id']),
                )
                draft_id = existing['id']
            else:
                cursor = conn.execute(
                    '''INSERT INTO platform_drafts
                       (content_id, platform, title, body, summary, tags, cover_image, extra_config, validation_warnings)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (content_id, draft['platform'], draft['title'], draft['body'], draft.get('summary', ''), tags, draft.get('cover_image', ''), extra_config, warnings),
                )
                draft_id = cursor.lastrowid
            conn.commit()
        return self.get(draft_id)

    def update(self, draft_id, data):
        current = self.get(draft_id)
        if not current:
            return None
        merged = {**current, **data}
        tags = json.dumps(merged.get('tags', []), ensure_ascii=False)
        extra_config = json.dumps(merged.get('extra_config', {}), ensure_ascii=False)
        warnings = json.dumps(merged.get('validation_warnings', []), ensure_ascii=False)
        with get_connection() as conn:
            conn.execute(
                '''UPDATE platform_drafts
                   SET title = ?, body = ?, summary = ?, tags = ?, cover_image = ?, extra_config = ?, validation_warnings = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (merged['title'], merged['body'], merged.get('summary', ''), tags, merged.get('cover_image', ''), extra_config, warnings, draft_id),
            )
            conn.commit()
        return self.get(draft_id)

    def _decode(self, row):
        if not row:
            return None
        row['tags'] = json.loads(row.get('tags') or '[]')
        row['extra_config'] = json.loads(row.get('extra_config') or '{}')
        row['validation_warnings'] = json.loads(row.get('validation_warnings') or '[]')
        return row
