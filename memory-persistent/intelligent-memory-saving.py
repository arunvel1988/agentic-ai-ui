"""
memory.py

Persistent + Semantic Agent Memory

Features:
- SQLite conversation history
- Long-term semantic memories
- Ollama embeddings
- Cosine similarity retrieval
- LLM-based decision about what deserves long-term memory
"""

import json
import math
import sqlite3
import requests
from datetime import datetime


class ConversationMemory:

    def __init__(
        self,
        db_path="/data/agent_memory.db",
        ollama_url="http://ollama:11434",
        embedding_model="nomic-embed-text",
        max_messages=20,
    ):
        self.db_path = db_path
        self.ollama_url = ollama_url
        self.embedding_model = embedding_model
        self.max_messages = max_messages

        self._create_tables()

    # =========================================================
    # DATABASE
    # =========================================================

    def _connect(self):
        return sqlite3.connect(
            self.db_path,
            timeout=10
        )

    def _create_tables(self):

        with self._connect() as conn:

            # Normal conversation history
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

            # Long-term semantic memory
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            conn.commit()

    # =========================================================
    # BASIC CONVERSATION HISTORY
    # =========================================================

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

    def add_user(self, message):

        self._add_message(
            "user",
            message
        )

    def add_assistant(self, message):

        self._add_message(
            "assistant",
            message
        )

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

        rows.reverse()

        if not rows:
            return "No previous conversation."

        result = ""

        for role, content in rows:

            if role == "user":
                result += f"User: {content}\n"

            else:
                result += f"Assistant: {content}\n"

        return result

    # =========================================================
    # EMBEDDINGS
    # =========================================================

    def _create_embedding(self, text):

        response = requests.post(
            f"{self.ollama_url}/api/embed",
            json={
                "model": self.embedding_model,
                "input": text
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data["embeddings"][0]

    # =========================================================
    # LONG-TERM MEMORY
    # =========================================================

    def add_memory(self, content):

        content = content.strip()

        if not content:
            return

        # Avoid storing exact duplicate memories
        with self._connect() as conn:

            existing = conn.execute(
                """
                SELECT id
                FROM memories
                WHERE content = ?
                """,
                (content,)
            ).fetchone()

        if existing:
            return

        embedding = self._create_embedding(content)

        with self._connect() as conn:

            conn.execute(
                """
                INSERT INTO memories (
                    content,
                    embedding,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    content,
                    json.dumps(embedding),
                    datetime.now().isoformat()
                )
            )

            conn.commit()

        print(f"[MEMORY SAVED] {content}")

    # =========================================================
    # COSINE SIMILARITY
    # =========================================================

    def _cosine_similarity(self, vector_a, vector_b):

        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = math.sqrt(
            sum(a * a for a in vector_a)
        )

        magnitude_b = math.sqrt(
            sum(b * b for b in vector_b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (
            magnitude_a * magnitude_b
        )

    # =========================================================
    # SEMANTIC SEARCH
    # =========================================================

    def search_memories(
        self,
        query,
        limit=5,
        threshold=0.45
    ):

        query_embedding = self._create_embedding(query)

        with self._connect() as conn:

            rows = conn.execute(
                """
                SELECT id, content, embedding
                FROM memories
                """
            ).fetchall()

        results = []

        for memory_id, content, embedding_json in rows:

            embedding = json.loads(
                embedding_json
            )

            score = self._cosine_similarity(
                query_embedding,
                embedding
            )

            if score >= threshold:

                results.append(
                    {
                        "id": memory_id,
                        "content": content,
                        "score": score
                    }
                )

        # Highest similarity first
        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:limit]

    # =========================================================
    # FORMAT RELEVANT MEMORY FOR LLM
    # =========================================================

    def relevant_memory(self, query):

        memories = self.search_memories(query)

        if not memories:
            return "No relevant long-term memory."

        result = ""

        for item in memories:

            result += (
                f"- {item['content']} "
                f"(similarity={item['score']:.2f})\n"
            )

        return result

    # =========================================================
    # CLEAR CONVERSATION
    # =========================================================

    def clear(self):

        with self._connect() as conn:

            conn.execute(
                "DELETE FROM messages"
            )

            conn.commit()

    # =========================================================
    # CLEAR LONG TERM MEMORY
    # =========================================================

    def clear_long_term_memory(self):

        with self._connect() as conn:

            conn.execute(
                "DELETE FROM memories"
            )

            conn.commit()

    # =========================================================
    # INSPECT MEMORIES
    # =========================================================

    def get_memories(self):

        with self._connect() as conn:

            rows = conn.execute(
                """
                SELECT id, content, created_at
                FROM memories
                ORDER BY id
                """
            ).fetchall()

        return rows


memory = ConversationMemory()
