from django.db import connection
from datetime import datetime

class UserModel:
    @staticmethod
    def create_user(first_name, last_name, email, password, phone, dob, gender, address, role_type, is_approved=False):
        """
        Creates a new user in the database.
        """
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, address, role_type, is_approved, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
            """
            cursor.execute(sql, (first_name, last_name, email, password, phone, dob, gender, address, role_type, is_approved))
            user_id = cursor.fetchone()[0]
            return user_id

    @staticmethod
    def create_approval_request(user_id, requested_by_id):
        """
        Creates an approval request for a user.
        """
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO approval_requests (user_id, requested_by_id, is_approved, created_at, updated_at)
                VALUES (%s, %s, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
            """
            cursor.execute(sql, (user_id, requested_by_id))
            return cursor.fetchone()[0]

    @staticmethod
    def get_user_by_email(email):
        """
        Retrieves a user by their email.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s;", [email])
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieves a user by their ID.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s;", [user_id])
            row = cursor.fetchone()
            if not row:
                return None
                
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

    @staticmethod
    def approve_user(user_id):
        """
        Approves a user account.
        """
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET is_approved = TRUE WHERE id = %s AND is_approved = FALSE;", [user_id])
            return cursor.rowcount  # Returns number of rows updated

    @staticmethod
    def get_pending_users():
        """
        Retrieves a list of users with pending approval requests.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, first_name, last_name, email, role_type, created_at 
                FROM users 
                WHERE is_approved = FALSE AND role_type IN ('super_admin', 'artist_manager')
                ORDER BY created_at DESC;
            """)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def get_pending_approval_requests():
        """
        Retrieves a list of pending approval requests.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ar.id, ar.user_id, ar.requested_by_id, ar.created_at, 
                       u.first_name, u.last_name, u.email, u.role_type
                FROM approval_requests ar
                JOIN users u ON ar.user_id = u.id
                WHERE ar.is_approved = FALSE
                ORDER BY ar.created_at DESC;
            """)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def approve_approval_request(request_id):
        """
        Approves an approval request and updates the user's status.
        """
        with connection.cursor() as cursor:
            # Approve the request
            cursor.execute("""
                UPDATE approval_requests 
                SET is_approved = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND is_approved = FALSE
                RETURNING user_id;
            """, [request_id])
            result = cursor.fetchone()
            if not result:
                return False

            user_id = result[0]

            # Approve the user
            cursor.execute("""
                UPDATE users 
                SET is_approved = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND is_approved = FALSE;
            """, [user_id])
            return cursor.rowcount > 0