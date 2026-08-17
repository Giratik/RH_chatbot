# frontend/main.py

import streamlit as st
import os
import datetime
from plugins.Styles import render_styles
from pages.Configuration import set_rag_stats

IS_DEV = os.environ.get("IS_DEV", "no")
LOGO_PATH = "ressource/Eau_de_Paris_bleu.svg.png"

# ─── PAGE CONFIG (Doit être le premier appel Streamlit) ───────────────
st.set_page_config(page_title="RAG Integrated", page_icon="🤖", layout="wide")

if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH)

render_styles()

# ─── FONCTION D'INITIALISATION ─────────────────────────────────────────
def init_session_state():
    if "system_prompt" not in st.session_state:
        mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        now = datetime.datetime.now()
        date_actuelle = f"{mois_fr[now.month - 1]} {now.year}"
        
        prompt = f"""Tu es un assistant IA expert, concis et professionnel.
Ta mission est de répondre à la question de l'utilisateur en utilisant UNIQUEMENT le contexte fourni ci-dessous.
Si la réponse n'est pas dans le contexte, dis poliment "Je ne trouve pas cette information dans les documents fournis", et n'invente rien.
Réponds en français.

RÈGLES IMPORTANTES :
- Nous sommes en {date_actuelle}.
- Les dates des documents sont indiquées entre crochets [Document du YYYY-MM-DD].
- Si plusieurs documents traitent le même sujet avec des dates différentes, PRIORISE TOUJOURS le document le plus récent et considère les autres comme caduques."""
        
        st.session_state.system_prompt = prompt
        st.session_state.default_system_prompt = prompt

    if "rag_config" not in st.session_state:
        st.session_state.rag_config = set_rag_stats()

    if "is_dev" not in st.session_state:
        st.session_state.is_dev = IS_DEV

# ─── ROUTAGE ET NAVIGATION ─────────────────────────────────────────────
def main():
    init_session_state()

    # Déclaration des pages
    page_chat = st.Page("pages/Chatbot_RH.py", title="Chat RH", icon="💬", default=True)
    page_changelog = st.Page("pages/Changelog.py", title="Changelog", icon="📝")
    page_config = st.Page("pages/Configuration.py", title="Configuration", icon="⚙️")
    page_test = st.Page("pages/test_retrieval.py", title="test rag")

    # Construction dynamique de la navigation
    pages_visibles = [page_chat]

    # Ajout conditionnel de la page de config
    if st.session_state.is_dev == "yes":
        pages_visibles.append(page_changelog)
        pages_visibles.append(page_config)
        pages_visibles.append(page_test)

    # Exécution de la navigation
    pg = st.navigation(pages_visibles)
    pg.run()

if __name__ == "__main__":
    main()