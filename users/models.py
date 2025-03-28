from django.db import connection
from datetime import datetime

class UserModel:
    
    @staticmethod
    def create_user(first_name, last_name, email, password, phone, dob, gender, address, role_type, is_approved=False):
        """
        Creates a new user in the database using raw SQL.
        """
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, address, role_type, is_approved, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
            """
            cursor.execute(sql, [first_name, last_name, email, password, phone, dob, gender, address, role_type, is_approved])
            return cursor.fetchone()[0]

    @staticmethod
    def create_approval_request(user_id, requested_by_id):
        """
        Creates an approval request for a user using raw SQL.
        """
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO approval_requests (user_id, requested_by_id, is_approved, created_at, updated_at)
                VALUES (%s, %s, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
            """
            cursor.execute(sql, [user_id, requested_by_id])
            return cursor.fetchone()[0]

    @staticmethod
    def get_user_by_email(email):
        """
        Retrieves a user by their email using raw SQL.
        """
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s;"
            cursor.execute(sql, [email])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieves a user by their ID using raw SQL.
        """
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s;"
            cursor.execute(sql, [user_id])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None

    @staticmethod
    def approve_user(user_id):
        """
        Approves a user account using raw SQL.
        """
        with connection.cursor() as cursor:
            sql = """
                UPDATE users 
                SET is_approved = TRUE, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s AND is_approved = FALSE
                RETURNING id;
            """
            cursor.execute(sql, [user_id])
            result = cursor.fetchone()
            return result is not None

    @staticmethod
    def get_pending_users():
        """
        Retrieves a list of users with pending approval requests using raw SQL.
        """
        with connection.cursor() as cursor:
            sql = """
                SELECT id, first_name, last_name, email, role_type, created_at 
                FROM users 
                WHERE is_approved = FALSE AND role_type IN ('super_admin', 'artist_manager')
                ORDER BY created_at DESC;
            """
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows] if rows else []

    @staticmethod
    def get_pending_approval_requests():
        """
        Retrieves a list of pending approval requests using raw SQL.
        """
        with connection.cursor() as cursor:
            sql = """
                SELECT ar.id, ar.user_id, ar.requested_by_id, ar.created_at, 
                       u.first_name, u.last_name, u.email, u.role_type
                FROM approval_requests ar
                JOIN users u ON ar.user_id = u.id
                WHERE ar.is_approved = FALSE
                ORDER BY ar.created_at DESC;
            """
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows] if rows else []

    @staticmethod
    def approve_approval_request(request_id):
        """
        Approves an approval request and updates the user's status using raw SQL.
        """
        with connection.cursor() as cursor:
            # Approve the request
            sql = """
                UPDATE approval_requests 
                SET is_approved = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND is_approved = FALSE
                RETURNING user_id;
            """
            cursor.execute(sql, [request_id])
            result = cursor.fetchone()
            if not result:
                return False  # Request not found or already approved

            user_id = result[0]

            # Approve the user
            sql = """
                UPDATE users 
                SET is_approved = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND is_approved = FALSE
                RETURNING id;
            """
            cursor.execute(sql, [user_id])
            return cursor.fetchone() is not None
            
    # New methods for dashboard functionality
    
    @staticmethod
    def get_total_users_count():
        """
        Returns the total count of users using raw SQL.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users;")
            return cursor.fetchone()[0]

    @staticmethod
    def get_approved_artists_count():
        """
        Returns the count of approved artists using raw SQL.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE role_type = 'artist' AND is_approved = TRUE;")
            return cursor.fetchone()[0]

    @staticmethod
    def get_artists_count():
        """
        Returns the total count of artists using raw SQL.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE role_type = 'artist';")
            return cursor.fetchone()[0]

    @staticmethod
    def get_pending_artists_count():
        """
        Returns the count of pending artists using raw SQL.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE role_type = 'artist' AND is_approved = FALSE;")
            return cursor.fetchone()[0]

    @staticmethod
    def get_artist_works(artist_id):
        """
        Returns the works of an artist using raw SQL.
        """
        with connection.cursor() as cursor:
            # Adjust this query based on your actual database schema for artist works
            cursor.execute("""
                SELECT * FROM artist WHERE user_id = %s 
                ORDER BY created_at DESC;
            """, [artist_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows] if rows else []