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

import streamlit as st
from plugins.Styles import render_styles
from plugins.Sidebar import render_save_chat
from plugins.Chat import render_chat

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="RAG Integrated", page_icon="🤖", layout="wide")

# Injection des styles CSS globaux
render_styles()

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    # Initialisation de l'état de session pour le chat RH
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Configuration RAG spécifique pour les RH 
    # Note : Cette configuration pourrait être externalisée dans un fichier de config
    cfg = {
        "collection": "dummy_rh",  # Collection ChromaDB contenant les documents RH
        "model": "gemma4:e4b",    # Modèle LLM utilisé pour les réponses RH
        "doc_date_filter": "",
        "n_results": 250,          # Nombre de chunks à récupérer
        "seuil": 0.6,              # Seuil de distance pour la pertinence
        "use_hyde": True,          # Utilisation de l'hypothèse de réponse
        "use_expansion": True,     # Expansion de requête avec synonymes
        "alpha": 0.5,              # Équilibre entre recherche vectorielle et BM25
    }

    # Configuration alternative : utiliser la sidebar pour la configuration RAG
    # cfg = render_sidebar()  # Décommenter pour permettre la configuration utilisateur

    # Affichage du titre
    st.title("Chatbot spécialisé question RH")

    # Rendu du composant de chat avec pipeline RAG
    # Ce composant gère :
    # - L'historique des messages
    # - La saisie utilisateur
    # - La recherche RAG dans les documents RH
    # - L'affichage des sources et citations
    render_chat(cfg)

    # Composant de sauvegarde/restauration des conversations
    # Identique à celui utilisé dans Main.py pour la cohérence
    render_save_chat()

if __name__ == "__main__":
    main()