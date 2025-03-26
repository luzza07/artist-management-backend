# core/db_utils.py
from django.db import connection

def dictfetchall(cursor):
    """Return all rows from cursor as dicts"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def execute_query(query, params=None):
    """Safe query execution wrapper"""
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return dictfetchall(cursor)