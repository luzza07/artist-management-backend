from django.db import connection
import uuid

class MusicModel:
    @classmethod
    def get_music_by_album(cls, album_id):
        """ Retrieve all music tracks associated with a specific album. """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM music
                WHERE album_id = %s
            """, [album_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    
    @classmethod
    @classmethod
    def create_music(cls, data):
        with connection.cursor() as cursor:
            # Generate a unique music_id
            music_id = str(uuid.uuid4())  # UUID as a unique identifier for music

            # Get the highest current track number for this album
            cursor.execute("""
                SELECT MAX(track_number) FROM music
                WHERE album_id = %s
            """, [data['album_id']])
            result = cursor.fetchone()
            next_track_number = result[0] + 1 if result[0] is not None else 1  # Default to 1 if no tracks exist

            # Insert the new track with the generated music_id and calculated track number
            cursor.execute("""
                INSERT INTO music (album_id, music_id, title, genre, track_number, duration, release_date, cover_page)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, album_id, music_id, title, genre, track_number, duration, release_date, cover_page
            """, [
                data['album_id'], 
                music_id,  # Insert the generated music_id
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
                SET music_id = %s,
                    title = %s,
                    genre = %s,
                    duration = %s,
                    release_date = %s,
                    cover_page = %s,
                    track_number = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND album_id = %s
                RETURNING id, album_id, music_id, title, genre, duration, release_date, cover_page, track_number
            """, [
                data.get('music_id'),
                data.get('title'),
                data.get('genre'),
                data.get('duration'),
                data.get('release_date'),
                data.get('cover_page'),
                data.get('track_number'),
                music_id,
                album_id
            ])
            result = cursor.fetchone()
            return dict(zip([col[0] for col in cursor.description], result)) if result else None

    @classmethod
    def delete_music(cls, music_id, album_id):
        with connection.cursor() as cursor:
            # Delete the track
            cursor.execute("""
                DELETE FROM music 
                WHERE id = %s AND album_id = %s
                RETURNING track_number
            """, [music_id, album_id])
            result = cursor.fetchone()

            if result:
                deleted_track_number = result[0]

                # Update subsequent tracks to shift their track_number down by 1
                cursor.execute("""
                    UPDATE music
                    SET track_number = track_number - 1
                    WHERE album_id = %s AND track_number > %s
                """, [album_id, deleted_track_number])

                return True
            return False
