"""
Simple Todo List REST API

This Flask application demonstrates basic REST API principles:
- GET /api/todos - Retrieve all todos
- POST /api/todos - Create a new todo
- DELETE /api/todos/<id> - Delete a todo

Data is stored in-memory (resets when server restarts).
In a real application, you would use a database.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger

import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "tododb"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )

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

# Initialize Flask application
app = Flask(__name__)

# Enable CORS to allow requests from frontend (different port/origin)
# Configure CORS to allow requests from any origin for development
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure Swagger UI for API documentation
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs"
}

swagger_template = {
    "info": {
        "title": "Todo List REST API",
        "description": "A simple REST API for managing todo items. This demonstrates basic CRUD operations using REST principles.",
        "version": "1.0.0"
    },
    "schemes": ["http"],
    "tags": [
        {
            "name": "todos",
            "description": "Todo item operations"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, text FROM todos;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    todos = [{'id': row[0], 'text': row[1]} for row in rows]
    return jsonify(todos), 200

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    if not data['text'].strip():
        return jsonify({'error': 'Text cannot be empty'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO todos (text) VALUES (%s) RETURNING id;", (data['text'].strip(),))
    todo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    new_todo = {'id': todo_id, 'text': data['text'].strip()}
    return jsonify(new_todo), 201

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s RETURNING id;", (todo_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if result is None:
        return jsonify({'error': 'Todo not found'}), 404
    return '', 204

@app.route('/')
def home():
    """
    Root endpoint - provides API information
    """
    return jsonify({
        'message': 'Todo List REST API',
        'endpoints': {
            'GET /api/todos': 'Get all todos',
            'POST /api/todos': 'Create a new todo',
            'DELETE /api/todos/<id>': 'Delete a todo'
        }
    })

# Run the application
if __name__ == '__main__':
    # debug=True enables auto-reload and detailed error messages
    # Don't use debug=True in production!
    print("Starting Flask server...")
    print("API will be available at: http://localhost:8000")
    print("\nAPI endpoints:")
    print("  GET    http://localhost:8000/api/todos")
    print("  POST   http://localhost:8000/api/todos")
    print("  DELETE http://localhost:8000/api/todos/<id>")
    print("\nSwagger API Documentation:")
    print("  http://localhost:8000/api-docs")
    print("  (Interactive API testing and documentation)")
    print("\nPress CTRL+C to stop the server")
    print("\nNote: Using port 8000 to avoid conflicts with system services")

    initialize_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
