import psycopg2
import os

def initialize_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "tododb"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )

def get_todos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, text FROM todos ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": row[0], "text": row[1]} for row in rows]

def create_todo(text):
    if not text:
        raise ValueError("Text is required")
    if len(text) > 200:
        raise ValueError("Text too long (max 200 characters)")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO todos (text) VALUES (%s) RETURNING id;", (text,))
    todo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": todo_id, "text": text}

def delete_todo(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s RETURNING id;", (todo_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if result is None:
        raise ValueError("Todo not found")
    return {"message": f"Todo with id {todo_id} deleted"}
