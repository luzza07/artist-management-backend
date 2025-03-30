
from django.db import connection

class MusicModel:
    @classmethod
    def get_music_by_album(cls, album_id):
        """ Retrieve all music tracks associated with a specific album. """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, album_id, title, genre, duration, release_date, cover_page, track_number, created_at, updated_at
                FROM music
                WHERE album_id = %s
            """, [album_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @classmethod
    def create_music(cls, data):
        with connection.cursor() as cursor:
            # Get the highest track number for this album
            cursor.execute("""
                SELECT MAX(track_number) FROM music WHERE album_id = %s
            """, [data['album_id']])
            result = cursor.fetchone()
            next_track_number = result[0] + 1 if result[0] is not None else 1  # Default to 1 if no tracks exist

            # Insert the new track
            cursor.execute("""
                INSERT INTO music (album_id, title, genre, track_number, duration, release_date, cover_page)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, album_id, title, genre, track_number, duration, release_date, cover_page
            """, [
                data['album_id'], 
                data['title'], 
                data['genre'],
                next_track_number,  # Use the calculated track number
                data['duration'],
                data['release_date'],
                data.get('cover_page')
            ])
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, cursor.fetchone()))

    @classmethod
    def update_music(cls, music_id, album_id, data):
        """ Update an existing music track's details. """
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE music
                SET title = %s,
                    genre = %s,
                    duration = %s,
                    release_date = %s,
                    cover_page = %s,
                    track_number = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND album_id = %s
                RETURNING id, album_id, title, genre, duration, release_date, cover_page, track_number
            """, [
                data.get('title'),
                data.get('genre'),
                data.get('duration'),
                data.get('release_date'),
                data.get('cover_page'),
                data.get('track_number'),
                music_id,  # Use `id` instead of `music_id`
                album_id
            ])
            result = cursor.fetchone()
            return dict(zip([col[0] for col in cursor.description], result)) if result else None

    @classmethod
    def delete_music(cls, music_id, album_id):
        """ Delete a music track and update track numbers. """
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM music 
                WHERE id = %s AND album_id = %s
                RETURNING track_number
            """, [music_id, album_id])
            result = cursor.fetchone()

            if result:
                deleted_track_number = result[0]

                # Shift subsequent tracks down
                cursor.execute("""
                    UPDATE music
                    SET track_number = track_number - 1
                    WHERE album_id = %s AND track_number > %s
                """, [album_id, deleted_track_number])

                return True
            return False
