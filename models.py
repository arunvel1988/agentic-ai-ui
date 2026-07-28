"""
models.py
----------
Wrapper around Ollama API.
"""

import requests
import json
import os


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b"
)


class Ollama:

    def __init__(self):
        self.url = f"{OLLAMA_URL}/api/generate"

    def generate(self, prompt):

        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        return data["response"].strip()


llm = Ollama()
