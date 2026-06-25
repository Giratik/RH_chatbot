"""
Chatbot_RH.py - Interface spécialisée RH
──────────────────────────────────────────────────────────
Rôle : Chatbot spécialisé avec accès à la base de connaissances RH
- Répond aux questions spécifiques sur les RH
- Utilise le pipeline RAG pour la recherche dans les documents RH
- Fournit des citations précises des sources RH
- Configuration RAG spécialisée

Architecture :
- Utilise Chat.py pour le composant de chat avec RAG
- Intègre Sidebar.py pour la sauvegarde des conversations
- Dépend des composants RAG et de la base de connaissances RH

Différence avec Main.py :
- Ce fichier est spécialisé pour les questions RH avec accès RAG
- Main.py est généraliste pour l'analyse de fichiers et demandes variées
- Ce chatbot nécessite une configuration RAG spécifique
"""
LOGO_PATH = "ressource/Eau_de_Paris_bleu.svg.png"


# frontend/main.py

import streamlit as st
import os
import datetime
from plugins.Styles import render_styles
from plugins.Sidebar import render_save_chat
from plugins.Chat import render_chat
from pages.Configuration import set_rag_stats

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="RAG Integrated", page_icon="🤖", layout="wide")

if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH)

render_styles()

# ─── FONCTION D'INITIALISATION ────────────────────────────────────────────────
def init_session_state():
    """S'assure que les variables de config sont présentes même si l'utilisateur
    ne visite pas la page de configuration en premier."""
    
    if "system_prompt" not in st.session_state:
        mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        now = datetime.datetime.now()
        date_actuelle = f"{mois_fr[now.month - 1]} {now.year}"
        
        st.session_state.system_prompt = f"""Tu es un assistant IA expert, concis et professionnel.
Ta mission est de répondre à la question de l'utilisateur en utilisant UNIQUEMENT le contexte fourni ci-dessous.
Si la réponse n'est pas dans le contexte, dis poliment "Je ne trouve pas cette information dans les documents fournis", et n'invente rien.
Réponds en français.

RÈGLES IMPORTANTES :
- Nous sommes en {date_actuelle}.
- Les dates des documents sont indiquées entre crochets [Document du YYYY-MM-DD].
- Si plusieurs documents traitent le même sujet avec des dates différentes, PRIORISE TOUJOURS le document le plus récent et considère les autres comme caduques."""
        st.session_state.default_system_prompt = f"""Tu es un assistant IA expert, concis et professionnel.
Ta mission est de répondre à la question de l'utilisateur en utilisant UNIQUEMENT le contexte fourni ci-dessous.
Si la réponse n'est pas dans le contexte, dis poliment "Je ne trouve pas cette information dans les documents fournis", et n'invente rien.
Réponds en français.

RÈGLES IMPORTANTES :
- Nous sommes en {date_actuelle}.
- Les dates des documents sont indiquées entre crochets [Document du YYYY-MM-DD].
- Si plusieurs documents traitent le même sujet avec des dates différentes, PRIORISE TOUJOURS le document le plus récent et considère les autres comme caduques."""

    if "rag_config" not in st.session_state:
        st.session_state.rag_config = set_rag_stats()



# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    # Initialisation de l'état de session pour le chat et la config
    init_session_state()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # On récupère le cfg dynamiquement depuis le session_state
    cfg = st.session_state.rag_config

    st.title("Chatbot spécialisé question RH")

    # Il faudra t'assurer que render_chat() prend aussi en compte le SYSTEM_PROMPT
    # Par exemple, en le passant dans le dictionnaire cfg ou en argument supplémentaire :
    # render_chat(cfg, st.session_state.system_prompt)
    render_chat(cfg) 

    render_save_chat()

if __name__ == "__main__":
    main()