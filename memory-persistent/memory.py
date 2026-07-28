"""
memory.py
---------

Persistent Conversation Memory using SQLite
"""

import sqlite3
from datetime import datetime


class ConversationMemory:

    def __init__(self, db_path="/data/agent_memory.db", max_messages=20):

        self.db_path = db_path
        self.max_messages = max_messages

        self._create_table()

    # -------------------------------------------------
    # Database Connection
    # -------------------------------------------------

    def _connect(self):

        return sqlite3.connect(
            self.db_path,
            timeout=10
        )

    # -------------------------------------------------
    # Create Table
    # -------------------------------------------------

    def _create_table(self):

        with self._connect() as conn:

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            conn.commit()

    # -------------------------------------------------
    # Add Message
    # -------------------------------------------------

    def _add_message(self, role, content):

        with self._connect() as conn:

            conn.execute(
                """
                INSERT INTO messages (
                    role,
                    content,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    role,
                    content,
                    datetime.now().isoformat()
                )
            )

            conn.commit()

    # -------------------------------------------------
    # User Message
    # -------------------------------------------------

    def add_user(self, message):

        self._add_message(
            "user",
            message
        )

    # -------------------------------------------------
    # Assistant Message
    # -------------------------------------------------

    def add_assistant(self, message):

        self._add_message(
            "assistant",
            message
        )

    # -------------------------------------------------
    # Conversation History
    # -------------------------------------------------

    def history(self):

        with self._connect() as conn:

            rows = conn.execute(
                """
                SELECT role, content
                FROM messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (self.max_messages,)
            ).fetchall()

        # Database returned newest first.
        # Reverse so LLM receives oldest -> newest.

        rows.reverse()

        if not rows:
            return "No previous conversation."

        conversation = ""

        for role, content in rows:

            if role == "user":
                conversation += f"User: {content}\n"

            elif role == "assistant":
                conversation += f"Assistant: {content}\n"

        return conversation

    # -------------------------------------------------
    # Get Messages
    # -------------------------------------------------

    def get_messages(self):

        with self._connect() as conn:

            rows = conn.execute(
                """
                SELECT id, role, content, created_at
                FROM messages
                ORDER BY id
                """
            ).fetchall()

        return rows

    # -------------------------------------------------
    # Clear Memory
    # -------------------------------------------------

    def clear(self):

        with self._connect() as conn:

            conn.execute(
                "DELETE FROM messages"
            )

            conn.commit()

    # -------------------------------------------------
    # Number of Messages
    # -------------------------------------------------

    def size(self):

        with self._connect() as conn:

            result = conn.execute(
                """
                SELECT COUNT(*)
                FROM messages
                """
            ).fetchone()

        return result[0]


memory = ConversationMemory()
