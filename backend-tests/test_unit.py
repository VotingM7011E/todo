import pytest
from unittest.mock import patch, Mock

# Add the path to the backend source code
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))

import todo_service


class TestGetTodos:
    @patch("todo_service.get_db_connection")
    def test_get_todos_returns_list(self, mock_get_db):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "Buy milk"), (2, "Walk dog")]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        todos = todo_service.get_todos()

        assert todos == [
            {"id": 1, "text": "Buy milk"},
            {"id": 2, "text": "Walk dog"},
        ]
        mock_cursor.execute.assert_called_once_with("SELECT id, text FROM todos ORDER BY id;")
        mock_conn.commit.assert_not_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestCreateTodo:
    def test_create_todo_empty_text_raises(self):
        with pytest.raises(ValueError, match="Text is required"):
            todo_service.create_todo("")

    def test_create_todo_text_too_long_raises(self):
        long_text = "a" * 201
        with pytest.raises(ValueError, match="Text too long"):
            todo_service.create_todo(long_text)

    @patch("todo_service.get_db_connection")
    def test_create_todo_success(self, mock_get_db):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = [42]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        result = todo_service.create_todo("Read a book")

        assert result == {"id": 42, "text": "Read a book"}
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO todos (text) VALUES (%s) RETURNING id;", ("Read a book",)
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestDeleteTodo:
    @patch("todo_service.get_db_connection")
    def test_delete_todo_success(self, mock_get_db):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = [1]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        result = todo_service.delete_todo(1)

        assert result == {"message": "Todo with id 1 deleted"}
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM todos WHERE id = %s RETURNING id;", (1,)
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("todo_service.get_db_connection")
    def test_delete_todo_not_found_raises(self, mock_get_db):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        with pytest.raises(ValueError, match="Todo not found"):
            todo_service.delete_todo(999)
