# frontend/main.py

import streamlit as st
import os
import datetime
from plugins.Styles import render_styles
#from pages.Configuration import set_rag_stats # tout se fait dans session_state_central_rh

from utility.session_state_central_rh import init_session_state, SK


IS_DEV = os.environ.get("IS_DEV", "no")
LLM_MODEL = os.environ.get("DEFAULT_LLM", "gemma4:e4b")
LOGO_PATH = "ressource/Eau_de_Paris_bleu.svg.png"





# ─── PAGE CONFIG (Doit être le premier appel Streamlit) ───────────────
st.set_page_config(page_title="Chatbot RH", layout="wide")

if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH)

render_styles()



# ─── ROUTAGE ET NAVIGATION ─────────────────────────────────────────────
def main():
    init_session_state(LLM_MODEL, is_dev=IS_DEV)

    # Déclaration des pages
    page_chat = st.Page("pages/Chatbot_RH.py", title="Chat RH", icon="💬", default=True)
    page_changelog = st.Page("pages/Changelog.py", title="Changelog", icon="📝")
    page_config = st.Page("pages/Configuration.py", title="Configuration", icon="⚙️")
    page_test = st.Page("pages/test_retrieval.py", title="test rag")

    # Construction dynamique de la navigation
    pages_visibles = [page_chat]
    pages_visibles.append(page_changelog)

    # Ajout conditionnel de la page de config
    if st.session_state.is_dev == "yes":
        
        pages_visibles.append(page_config)
        pages_visibles.append(page_test)

    # Exécution de la navigation
    pg = st.navigation(pages_visibles)
    pg.run()

if __name__ == "__main__":
    main()