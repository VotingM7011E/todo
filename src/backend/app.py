from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from
from todo_service import get_todos, create_todo, delete_todo, initialize_db

app = Flask(__name__)
CORS(app)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Todo List API",
        "description": "API for managing a simple todo list",
        "version": "1.0.0"
    },
    "basePath": "/",
    "tags": [
        {
            "name": "Todos",
            "description": "Operations related to todo items"
        }
    ]
}

swagger = Swagger(app, template=swagger_template)

@app.route("/api/todos", methods=["GET"])
@swag_from({
    "tags": ["Todos"],
    "summary": "Get all todos",
    "description": "Retrieve a list of all todo items.",
    "responses": {
        "200": {
            "description": "A list of todo items",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "text": {"type": "string"}
                    }
                }
            }
        }
    }
})
def list_todos():
    return jsonify(get_todos()), 200

@app.route("/api/todos", methods=["POST"])
@swag_from({
    "tags": ["Todos"],
    "summary": "Create a new todo",
    "description": "Add a new todo item to the list.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Todo item created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "text": {"type": "string"}
                }
            }
        },
        "400": {
            "description": "Invalid input"
        }
    }
})
def add_todo():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing text field"}), 400
    try:
        new_todo = create_todo(data["text"].strip())
        return jsonify(new_todo), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
@swag_from({
    "tags": ["Todos"],
    "summary": "Delete a todo",
    "description": "Delete a todo item by its ID.",
    "parameters": [
        {
            "name": "todo_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID of the todo item to delete"
        }
    ],
    "responses": {
        "204": {
            "description": "Todo item deleted successfully"
        },
        "404": {
            "description": "Todo item not found"
        }
    }
})
def remove_todo(todo_id):
    try:
        delete_todo(todo_id)
        return jsonify({"message": f"Todo with id {todo_id} deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

@app.route("/")
def home():
    return jsonify({
        "message": "Todo List REST API",
        "endpoints": {
            "GET /api/todos": "Get all todos",
            "POST /api/todos": "Create a new todo",
            "DELETE /api/todos/<id>": "Delete a todo"
        }
    })

if __name__ == "__main__":
    initialize_db()
    app.run(debug=True, host="0.0.0.0", port=8000)
