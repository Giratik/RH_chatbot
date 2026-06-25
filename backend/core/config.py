#backend/core/config.py

"""
Module : Configuration Globale
Description : Centralise les variables d'environnement, les configurations des clés API,
            les chemins des dossiers locaux et les paramètres par défaut du chatbot.
"""

import os

CONTEXT_SIZE = int(os.environ.get("CONTEXT_SIZE", 30000))
URL_OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8100))
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "embeddinggemma:latest")


SYSTEM_PROMPT = """
Tu es un assistant IA expert, concis et professionnel.
Ta mission est de répondre à la question de l'utilisateur en utilisant UNIQUEMENT le contexte fourni ci-dessous.
Si la réponse n'est pas dans le contexte, dis poliment "Je ne trouve pas cette information dans les documents fournis", et n'invente rien.
Réponds en français.

RÈGLES IMPORTANTES :
- Nous sommes en juin 2026.
- Les dates des documents sont indiquées entre crochets [Document du YYYY-MM-DD].
- Si plusieurs documents traitent le même sujet avec des dates différentes, PRIORISE TOUJOURS le document le plus récent et considère les autres comme caduques.
"""