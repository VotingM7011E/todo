import unittest
from unittest.mock import patch
from flask import json

# Add the path to the backend source code
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))

from app import app


class TestTodoAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.get_todos")
    def test_get_todos(self, mock_get_todos):
        mock_get_todos.return_value = [
            {"id": 1, "text": "Buy milk"},
            {"id": 2, "text": "Walk dog"},
        ]

        response = self.client.get("/api/todos")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [
            {"id": 1, "text": "Buy milk"},
            {"id": 2, "text": "Walk dog"},
        ])
        mock_get_todos.assert_called_once()

    @patch("app.create_todo")
    def test_create_todo(self, mock_create_todo):
        mock_create_todo.return_value = {"id": 3, "text": "Read book"}

        response = self.client.post("/api/todos", json={"text": "Read book"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data, {"id": 3, "text": "Read book"})
        mock_create_todo.assert_called_once_with("Read book")

    @patch("app.delete_todo")
    def test_delete_todo(self, mock_delete_todo):
        mock_delete_todo.return_value = {"message": "Todo with id 1 deleted"}

        response = self.client.delete("/api/todos/1")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {"message": "Todo with id 1 deleted"})
        mock_delete_todo.assert_called_once_with(1)
