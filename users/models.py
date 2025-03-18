from django.db import connection
from datetime import datetime

class UserModel:
    @staticmethod
    def create_user(first_name, last_name, email, password, phone, dob, gender, address, role_type):
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, address, role_type, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
            """
            cursor.execute(sql, (first_name, last_name, email, password, phone, dob, gender, address, role_type))
            return cursor.fetchone()[0]

    @staticmethod
    def get_user_by_email(email):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s;", [email])
            return cursor.fetchone()

    @staticmethod
    def get_user_by_id(user_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s;", [user_id])
            return cursor.fetchone()
