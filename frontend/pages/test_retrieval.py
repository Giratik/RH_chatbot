import streamlit as st
import requests
import json
import os

BASE_URL = os.getenv("API_URL", os.getenv("RAG_API_URL", "http://localhost:8000"))
CONTEXT_SIZE = int(os.environ.get("CONTEXT_SIZE", 22000))
# L'API backend est exposée sur le port 8002 sur ta machine hôte selon ton docker-compose
DEFAULT_API_URL = f"{BASE_URL}/rag"
DEFAULT_MODEL = "gemma4:e4b"

st.set_page_config(page_title="Testeur de Retrieval - Chatbot EDP", page_icon="🔍", layout="wide")

st.title("🔍 Testeur de Retrieval Qdrant")
st.markdown("Interface de débogage pour tester la récupération hybride (Vectoriel + BM25) du backend FastAPI.")

# ─── BARRE LATÉRALE : CONFIGURATION ───
with st.sidebar:
    st.header("⚙️ Configuration API")
    api_url = st.text_input("URL de base de l'API", value=DEFAULT_API_URL)
    model = st.text_input("Modèle d'embedding/LLM", value=DEFAULT_MODEL)
    
    st.divider()
    
    st.header("🗂️ Collections")
    if st.button("🔄 Charger les collections"):
        try:
            res = requests.get(f"{api_url}/collections")
            if res.status_code == 200:
                st.session_state["collections"] = res.json().get("collections", [])
                st.success("Collections chargées !")
            else:
                st.error(f"Erreur HTTP {res.status_code}")
        except Exception as e:
            st.error(f"Impossible de joindre l'API : {e}")

    collections = st.session_state.get("collections", [])
    selected_collection = st.selectbox("Collection à interroger", options=collections if collections else ["Aucune collection chargée"])
    
    # ─── NOUVEAU BOUTON : CHUNK ALÉATOIRE ───
    if selected_collection and selected_collection != "Aucune collection chargée":
        if st.button("🎲 Afficher un chunk aléatoire", use_container_width=True):
            with st.spinner("Récupération..."):
                try:
                    res_rand = requests.get(f"{api_url}/collections/{selected_collection}/random")
                    if res_rand.status_code == 200:
                        chunk_data = res_rand.json().get("chunk")
                        if chunk_data:
                            st.session_state["random_chunk"] = chunk_data
                        else:
                            st.warning("La collection semble vide.")
                    else:
                        st.error(f"Erreur API : {res_rand.status_code}")
                except Exception as e:
                    st.error(f"Erreur de connexion : {e}")
                    
    st.divider()
    
    st.header("🎛️ Paramètres de recherche")
    n_results = st.slider("Nombre de résultats (n_results)", 1, 20, 5)
    seuil = st.slider("Seuil de distance vectorielle max", 0.1, 2.0, 0.5, 0.05)
    alpha = st.slider("Alpha (1=Vectoriel pur, 0=BM25 pur)", 0.0, 1.0, 0.5, 0.1)
    use_hyde = st.checkbox("Utiliser HyDE (Génération de réponse hypothétique)", value=False)
    use_expansion = st.checkbox("Utiliser l'expansion de requête (Synonymes)", value=False)
    doc_date_filter = st.text_input("Filtre de date (optionnel)", placeholder="Ex: 2024-01-01")

# ─── AFFICHAGE DU CHUNK ALÉATOIRE (S'il y en a un) ───
if "random_chunk" in st.session_state:
    st.info("💡 **Aperçu d'un document stocké dans Qdrant :**")
    with st.expander("Voir le chunk aléatoire complet", expanded=True):
        payload = st.session_state["random_chunk"]
        
        # Affichage formaté si c'est un PDF
        if payload.get("content_type") == "pdf":
            st.markdown(f"**Source :** `{payload.get('source', 'Inconnue')}` (Page {payload.get('page', '?')})")
            st.markdown(f"**Date du document :** `{payload.get('doc_date', 'N/A')}`")
            st.text_area("Texte extrait", value=payload.get("document", ""), height=150, disabled=True)
        # Affichage formaté si c'est le lexique
        elif payload.get("content_type") == "lexique":
            st.markdown(f"**Acronyme :** `{payload.get('acronyme', '')}`")
            st.markdown(f"**Signification :** `{payload.get('signification', '')}`")
        
        # Le JSON brut en dessous
        st.json(payload)
    st.divider()

# ─── ZONE PRINCIPALE : RECHERCHE ───
query = st.text_area("Question de l'utilisateur", placeholder="Tape ta question ici...")

if st.button("🚀 Lancer le Retrieval", type="primary"):
    if selected_collection == "Aucune collection chargée" or not selected_collection:
        st.warning("Veuillez d'abord charger et sélectionner une collection dans la barre latérale.")
    elif not query:
        st.warning("Veuillez entrer une question.")
    else:
        payload = {
            "collection_name": selected_collection,
            "query": query,
            "model": model,
            "context_size": CONTEXT_SIZE,
            "n_results": n_results,
            "seuil": seuil,
            "alpha": alpha,
            "use_hyde": use_hyde,
            "use_expansion": use_expansion,
            "doc_date_filter": doc_date_filter
        }
        
        with st.spinner("Recherche en cours dans Qdrant via le backend..."):
            try:
                response = requests.post(f"{api_url}/search", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success(f"Recherche terminée en succès ! {len(data.get('sources', []))} document(s) trouvé(s).")
                    
                    tab1, tab2, tab3 = st.tabs(["📄 Sources extraites", "📝 Contextes formatés", "⚙️ Données brutes (JSON)"])
                    
                    with tab1:
                        if data.get("sources"):
                            for src in data["sources"]:
                                st.markdown(f"- **{src[0]}** (Score Hybride: `{src[1]:.4f}`, Distance Vecto: `{src[2]:.4f}`)")
                        else:
                            st.info("Aucune source trouvée. Essaie d'augmenter le seuil de distance.")
                            
                    with tab2:
                        if data.get("contexts"):
                            for ctx in data["contexts"]:
                                st.code(ctx, language="text")
                        else:
                            st.info("Aucun contexte généré.")
                            
                    with tab3:
                        st.json(data)
                        
                else:
                    st.error(f"Erreur de l'API (Code {response.status_code})")
                    st.json(response.json())
                    
            except Exception as e:
                st.error(f"Erreur lors de la communication avec le backend : {e}")