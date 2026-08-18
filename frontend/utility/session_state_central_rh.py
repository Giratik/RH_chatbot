# frontend/utility/session_state_central.py

import datetime
import re
from typing import Any
import streamlit as st
import os

from plugins.wrapper_API import get_registry_collection

API_URL = os.environ.get("API_URL", "http://backend:8000")

# ─── Constantes (noms des clés) ───────────────────────────────────────────────

class SK:
    """Session Keys — toutes les clés en un seul endroit."""

    # Conversation
    MESSAGES               = "messages"
    LAST_CHUNKS            = "last_chunks"

    # RAG
    RAG_CONFIG             = "rag_config"

    # Prompt système
    SYSTEM_PROMPT          = "system_prompt"
    DEFAULT_SYSTEM_PROMPT  = "default_system_prompt"

    # Mode développeur
    IS_DEV                 = "is_dev"

    # Collections
    COLLECTIONS            = "collections"


# ─── Factories dynamiques ─────────────────────────────────────────────────────
# Ces valeurs ne peuvent pas être calculées à l'import (dépendent du runtime),
# elles sont donc encapsulées dans des fonctions appelées à l'init.

def _build_system_prompt() -> str:
    """Construit le prompt système avec la date courante."""
    mois_fr = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
    ]
    now = datetime.datetime.now()
    date_actuelle = f"{mois_fr[now.month - 1]} {now.year}"

    return f"""Tu es un assistant IA expert, concis et professionnel.
Ta mission est de répondre à la question de l'utilisateur en utilisant UNIQUEMENT le contexte fourni ci-dessous.
Si la réponse n'est pas dans le contexte, dis poliment "Je ne trouve pas cette information dans les documents fournis", et n'invente rien.
Réponds en français.

RÈGLES IMPORTANTES :
- Nous sommes en {date_actuelle}.
- Les dates des documents sont indiquées entre crochets [Document du YYYY-MM-DD].
- Si plusieurs documents traitent le même sujet avec des dates différentes, PRIORISE TOUJOURS le document le plus récent et considère les autres comme caduques."""


def _build_rag_config(llm_model) -> dict:
    """Construit la config RAG en détectant la collection RH disponible."""
    registry = get_registry_collection().get("registry", [])
    collections_disponibles = [e["nom"] for e in registry]

    if not collections_disponibles:
        collection = "aucune_collection"
    else:
        match = next(
            (c for c in collections_disponibles if re.search(r"collection_rh", c, re.IGNORECASE)),
            None,
        )
        collection = match if match else collections_disponibles[0]

    return {
        "collection":      collection,
        "model":           llm_model,
        "doc_date_filter": "",
        "n_results":       250,
        "seuil":           0.6,
        "use_hyde":        True,
        "use_expansion":   True,
        "alpha":           0.5,
    }


# ─── Valeurs par défaut ───────────────────────────────────────────────────────
# Les callables sont invoquées à l'init (jamais à l'import).
# _build_system_prompt et _build_rag_config sont marquées comme "runtime" :
# elles ne figurent PAS dans _DEFAULTS car elles nécessitent IS_DEV en paramètre
# ou un appel réseau — elles sont gérées explicitement dans init_session_state().

_DEFAULTS: dict[str, Any] = {
    SK.MESSAGES:    list,   # ✅ factory
    SK.LAST_CHUNKS: list,   # ✅ factory
    SK.COLLECTIONS: list,   # ✅ factory
    # SK.SYSTEM_PROMPT, SK.DEFAULT_SYSTEM_PROMPT, SK.RAG_CONFIG, SK.IS_DEV
    # → initialisés explicitement dans init_session_state()
}


# ─── Initialisation ───────────────────────────────────────────────────────────

def init_session_state(llm_model: str, is_dev: bool = False) -> None:
    """À appeler une seule fois au démarrage (main.py)."""

    # Clés simples via _DEFAULTS
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default() if callable(default) else default

    # Prompt système — calcul dynamique (date courante)
    if SK.SYSTEM_PROMPT not in st.session_state:
        prompt = _build_system_prompt()
        st.session_state[SK.SYSTEM_PROMPT]        = prompt
        st.session_state[SK.DEFAULT_SYSTEM_PROMPT] = prompt

    # Config RAG — appel réseau pour détecter la collection
    if SK.RAG_CONFIG not in st.session_state:
        st.session_state[SK.RAG_CONFIG] = _build_rag_config(llm_model)

    # Mode développeur — valeur passée par main.py
    if SK.IS_DEV not in st.session_state:
        st.session_state[SK.IS_DEV] = is_dev


# ─── Accesseurs ───────────────────────────────────────────────────────────────

def get(key: str) -> Any:
    return st.session_state.get(key)

def set(key: str, value: Any) -> None:
    st.session_state[key] = value


# ─── Resets ciblés ────────────────────────────────────────────────────────────

def reset_conversation() -> None:
    """Efface la conversation sans toucher à la config."""
    st.session_state[SK.MESSAGES]    = []
    st.session_state[SK.LAST_CHUNKS] = []

def reset_rag_config(llm_model) -> None:
    """Remet la config RAG à ses valeurs par défaut (rappel réseau inclus)."""
    st.session_state[SK.RAG_CONFIG] = _build_rag_config(llm_model)

def reset_system_prompt() -> None:
    """Remet le prompt système à sa valeur par défaut."""
    st.session_state[SK.SYSTEM_PROMPT] = st.session_state[SK.DEFAULT_SYSTEM_PROMPT]

def reset_all(llm_model, is_dev: bool = False) -> None:
    """Réinitialise complètement la session frontend."""
    for key, default in _DEFAULTS.items():
        st.session_state[key] = default() if callable(default) else default

    prompt = _build_system_prompt()
    st.session_state[SK.SYSTEM_PROMPT]        = prompt
    st.session_state[SK.DEFAULT_SYSTEM_PROMPT] = prompt
    st.session_state[SK.RAG_CONFIG]            = _build_rag_config(llm_model)
    st.session_state[SK.IS_DEV]                = is_dev
    st.rerun()