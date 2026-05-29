from utils.db import fetch_data, execute_query

def authenticate(username, password):
    """
    Authenticates a user against the database.
    Returns a tuple (username, role, full_name, department) if valid, otherwise None.
    """
    query = """
    SELECT username, role, full_name, department
    FROM users
    WHERE username = %s AND password = %s
    """
    df = fetch_data(query, (username, password))
    if not df.empty:
        row = df.iloc[0]
        return (row['username'], row['role'], row['full_name'], row['department'])
    return None

def username_exists(username):
    query = "SELECT 1 FROM users WHERE username = %s"
    df = fetch_data(query, (username,))
    return not df.empty

def register_user(username, password, full_name, role='technician', department='Maintenance'):
    query = """
    INSERT INTO users (username, password, role, full_name, department)
    VALUES (%s, %s, %s, %s, %s)
    """
    execute_query(query, (username, password, role, full_name, department))

