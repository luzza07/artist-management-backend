from django.db import connection

class ArtistModel:
    @staticmethod
    def create_artist(user_id, first_release_year=None, photo_url=None):
        """
        Create an artist entry linked to a user
        """
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO artist (user_id, first_release_year, photo_url, created_at, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id;
            """
            cursor.execute(sql, [user_id, first_release_year, photo_url])
            return cursor.fetchone()[0]

    @staticmethod
    def get_artist_by_user_id(user_id):
        """
        Retrieve artist details by user ID
        """
        with connection.cursor() as cursor:
            sql = """
            SELECT a.*, u.first_name, u.last_name, u.email 
            FROM artist a
            JOIN users u ON a.user_id = u.id
            WHERE a.user_id = %s;
            """
            cursor.execute(sql, [user_id])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None

    @staticmethod
    def update_artist_profile(artist_id, **kwargs):
        """
        Update artist profile details
        """
        allowed_fields = ['first_release_year', 'photo_url']
        update_fields = [f"{field} = %s" for field in kwargs.keys() if field in allowed_fields]
        
        if not update_fields:
            return False

        with connection.cursor() as cursor:
            sql = f"""
            UPDATE artist 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            params = list(kwargs.values()) + [artist_id]
            cursor.execute(sql, params)
            return cursor.rowcount > 0


class AlbumModel:
    @staticmethod
    def create_album(artist_id, name, release_year, photo_url=None):
        """
        Create an album for an artist
        """
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO albums (artist_id, name, release_year, photo_url, created_at, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id;
            """
            cursor.execute(sql, [artist_id, name, release_year, photo_url])
            return cursor.fetchone()[0]

    @staticmethod
    def get_artist_albums(artist_id):
        """
        Retrieve all albums for a specific artist
        """
        with connection.cursor() as cursor:
            sql = """
            SELECT * FROM albums 
            WHERE artist_id = %s 
            ORDER BY release_year DESC;
            """
            cursor.execute(sql, [artist_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def update_album(album_id, **kwargs):
        """
        Update album details
        """
        allowed_fields = ['name', 'release_year', 'photo_url']
        update_fields = [f"{field} = %s" for field in kwargs.keys() if field in allowed_fields]
        
        if not update_fields:
            return False

        with connection.cursor() as cursor:
            sql = f"""
            UPDATE albums 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            params = list(kwargs.values()) + [album_id]
            cursor.execute(sql, params)
            return cursor.rowcount > 0


class MusicModel:
    @staticmethod
    def create_track(album_id, artist_id, title, genre, file_path=None):
        """
        Create a music track
        """
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO music (album_id, artist_id, title, genre, created_at, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id;
            """
            cursor.execute(sql, [album_id, artist_id, title, genre])
            return cursor.fetchone()[0]

    @staticmethod
    def get_album_tracks(album_id):
        """
        Retrieve all tracks for a specific album
        """
        with connection.cursor() as cursor:
            sql = """
            SELECT * FROM music 
            WHERE album_id = %s 
            ORDER BY created_at DESC;
            """
            cursor.execute(sql, [album_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def update_track(track_id, **kwargs):
        """
        Update track details
        """
        allowed_fields = ['title', 'genre', 'file_path']
        update_fields = [f"{field} = %s" for field in kwargs.keys() if field in allowed_fields]
        
        if not update_fields:
            return False

        with connection.cursor() as cursor:
            sql = f"""
            UPDATE music 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            params = list(kwargs.values()) + [track_id]
            cursor.execute(sql, params)
            return cursor.rowcount > 0