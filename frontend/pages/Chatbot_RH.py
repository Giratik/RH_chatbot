"""
Chatbot_RH.py - Interface spécialisée RH
"""
import streamlit as st
from plugins.Sidebar import render_save_chat
from plugins.Chat import render_chat

if "messages" not in st.session_state:
    st.session_state.messages = []

# On récupère le cfg dynamiquement depuis le session_state
cfg = st.session_state.rag_config

st.title("Chatbot spécialisé question RH")

# Affichage du chat
render_chat(cfg) 

# Affichage de la sauvegarde dans la sidebar
render_save_chat()