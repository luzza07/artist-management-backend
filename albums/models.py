from django.db import connection

class AlbumModel:
    @classmethod
    def get_albums_by_artist(cls, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, artist_id, name, release_year, genre, photo_url, tracklist, total_tracks, total_duration, created_at, updated_at
                FROM albums
                WHERE artist_id = %s
                ORDER BY created_at DESC
            """, [artist_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @classmethod
    def create_album(cls, artist_id, data):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO albums (artist_id, name, release_year, genre, photo_url, tracklist, total_tracks, total_duration)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, artist_id, name, release_year, genre, photo_url, tracklist, total_tracks, total_duration, created_at, updated_at
            """, [
                artist_id, 
                data['name'], 
                data['release_year'], 
                data['genre'], 
                data.get('photo_url'), 
                data.get('tracklist', []),  # Default empty list if not provided
                data.get('total_tracks', 0),  # Default 0 if not provided
                data.get('total_duration', '00:00:00')  # Default '00:00:00' if not provided
            ])
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, cursor.fetchone()))
    
    @classmethod
    def update_album(cls, album_id, artist_id, data):
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE albums 
                SET name = %s, 
                    release_year = %s, 
                    genre = %s,
                    photo_url = %s,
                    tracklist = %s,
                    total_tracks = %s,
                    total_duration = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND artist_id = %s
                RETURNING id, artist_id, name, release_year, genre, photo_url, tracklist, total_tracks, total_duration, created_at, updated_at
            """, [
                data.get('name'), 
                data.get('release_year'), 
                data.get('genre'),
                data.get('photo_url'),
                data.get('tracklist', []),  # Default empty list if not provided
                data.get('total_tracks', 0),  # Default 0 if not provided
                data.get('total_duration', '00:00:00'),  # Default '00:00:00' if not provided
                album_id,
                artist_id
            ])
            result = cursor.fetchone()
            return dict(zip([col[0] for col in cursor.description], result)) if result else None
    
    @classmethod
    def delete_album(cls, album_id, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM albums 
                WHERE id = %s AND artist_id = %s
                RETURNING id
            """, [album_id, artist_id])
            return cursor.fetchone() is not None
