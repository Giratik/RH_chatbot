"""
Chatbot_RH.py - Interface spécialisée RH
"""
import streamlit as st
from chatbot_utils.Sidebar import render_save_chat
from chatbot_utils.Chat import render_chat
from utility.session_state_central_rh import SK, get

#if "messages" not in st.session_state:
#    st.session_state.messages = []

# On récupère le cfg dynamiquement depuis le session_state
cfg = get(SK.RAG_CONFIG)

st.title("Chatbot spécialisé question RH")

# Affichage du chat
render_chat(cfg) 

# Affichage de la sauvegarde dans la sidebar
render_save_chat()