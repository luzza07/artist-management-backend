from django.db import connection
class MusicModel:
    @classmethod
    def get_music_by_album(cls, album_id, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.id, m.album_id, m.title, m.genre
                FROM music m
                JOIN albums a ON m.album_id = a.id
                WHERE m.album_id = %s AND a.artist_id = %s
                ORDER BY m.created_at DESC
            """, [album_id, artist_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @classmethod
    def create_music(cls, data):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO music (album_id, title, genre)
                VALUES (%s, %s, %s)
                RETURNING id, album_id, title, genre
            """, [
                data['album_id'], 
                data['title'], 
                data['genre']
            ])
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, cursor.fetchone()))
    
    @classmethod
    def update_music(cls, music_id, album_id, data):
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE music 
                SET title = %s, 
                    genre = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND album_id = %s
                RETURNING id, album_id, title, genre
            """, [
                data.get('title'), 
                data.get('genre'),
                music_id,
                album_id
            ])
            result = cursor.fetchone()
            return dict(zip([col[0] for col in cursor.description], result)) if result else None
    
    @classmethod
    def delete_music(cls, music_id, album_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM music 
                WHERE id = %s AND album_id = %s
                RETURNING id
            """, [music_id, album_id])
            return cursor.fetchone() is not None