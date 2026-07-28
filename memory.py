"""
memory.py
---------

Simple Conversation Memory
"""

from collections import deque


class ConversationMemory:
    def __init__(self, max_messages=20):
        """
        max_messages:
            Maximum number of messages to keep.
            (User + Assistant messages)
        """
        self.messages = deque(maxlen=max_messages)

    def add_user(self, message: str):
        """Store a user message."""
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_assistant(self, message: str):
        """Store an assistant message."""
        self.messages.append({
            "role": "assistant",
            "content": message
        })

    def history(self) -> str:
        """
        Return conversation history as a formatted string.
        """

        if not self.messages:
            return "No previous conversation."

        history = ""

        for msg in self.messages:

            if msg["role"] == "user":
                history += f"User: {msg['content']}\n"

            elif msg["role"] == "assistant":
                history += f"Assistant: {msg['content']}\n"

        return history

    def clear(self):
        """Clear all conversation history."""
        self.messages.clear()

    def get_messages(self):
        """Return messages as a list."""
        return list(self.messages)

    def size(self):
        """Return total messages stored."""
        return len(self.messages)


# Global Memory Instance
memory = ConversationMemory()
