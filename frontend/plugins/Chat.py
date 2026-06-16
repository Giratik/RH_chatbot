"""
plugins/Chat.py - Composant de Chat RAG Spécialisé RH
────────────────────────────────────────────────────
Rôle : Fournit l'interface de chat avec pipeline RAG pour les questions RH

Ce composant est spécialisé pour :
- Le chatbot RH (Chatbot_RH.py)
- L'accès à la base de connaissances RH 
- La recherche hybride dans les documents RH
- L'affichage des sources et citations

Architecture :
- Utilisé uniquement par Chatbot_RH.py (contrairement à general_purpose_chat_ui.py)
- Dépend de APIclient.py pour la communication avec le backend RAG
- Fournit des fonctionnalités spécifiques RH (citations, sources, etc.)

Différence avec general_purpose_chat_ui.py :
- Ce fichier est spécialisé pour les questions RH avec accès RAG
- general_purpose_chat_ui.py gère les demandes générales et l'analyse de fichiers
- Ce composant nécessite une configuration RAG spécifique
"""

import re
import streamlit as st
from plugins import APIclient as api

def _render_sources(citations: list[str]) -> None:
    """
    Affiche les sources citées dans un expander sous la réponse.
    Fonction utilitaire pour afficher les références des documents RH.

    Args:
        citations: Liste des citations à afficher
    """
    if not citations:
        return
    with st.expander(f"📚 Sources citées ({len(citations)})", expanded=False):
        for src in citations:
            st.markdown(f"- 📄 {src}")

def render_chat(cfg: dict) -> None:
    """
    Affiche la colonne de chat et exécute le pipeline RAG à chaque message.
    Fonction principale pour le chatbot RH spécialisé.

    Args:
        cfg: Dictionnaire de configuration RAG contenant :
             - collection: Nom de la collection ChromaDB
             - model: Modèle LLM à utiliser
             - doc_date_filter: Filtre par date de document
             - n_results: Nombre de chunks à récupérer
             - seuil: Seuil de distance pour la pertinence
             - use_hyde: Utilisation de l'hypothèse de réponse
             - use_expansion: Expansion de requête avec synonymes
             - alpha: Équilibre entre recherche vectorielle et BM25

    Pipeline RAG complet :
    1. Réécriture contextuelle de la requête
    2. Recherche hybride dans les documents RH
    3. Génération streamée de la réponse
    4. Extraction et affichage des sources citées
    """
    #st.markdown("### 💬 Conversation")

    # ── Historique affiché ────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                _render_sources(msg["citations"])

    if not (prompt := st.chat_input("Posez une question sur vos documents...")):
        return

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        # ── 1. Réécriture contextuelle ────────────────────────────────────────
        history_for_rewrite = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]
        try:
            standalone_query = api.rewrite_query(
                query=prompt,
                model=cfg["model"],
                chat_history=history_for_rewrite,
            )
        except Exception as e:
            st.error(f"Erreur lors de la réécriture : {e}")
            return

        # Afficher le badge seulement si la reformulation apporte un vrai changement
        # (on ignore la ponctuation, la casse et les espaces superflus)
        def _normalize(s: str) -> str:
            return re.sub(r"[^\w\s]", "", s.lower()).split()

        if _normalize(standalone_query) != _normalize(prompt):
            st.markdown(
                f"<div class='rewrite-badge'>🔄 Query : {standalone_query}</div>",
                unsafe_allow_html=True,
            )

        # ── 2. Recherche hybride ──────────────────────────────────────────────
        with st.status("🔍 Recherche dans les documents...", expanded=True) as status:
            try:
                contexts, sources, detailed_chunks = api.retrieve_context_hybrid(
                    collection_name=cfg["collection"],
                    query=standalone_query,
                    model=cfg["model"],
                    n_results=cfg["n_results"],
                    seuil=cfg["seuil"],
                    alpha=cfg["alpha"],
                    use_hyde=cfg["use_hyde"],
                    use_expansion=cfg["use_expansion"],
                    doc_date_filter=cfg.get("doc_date_filter", ""),
                )
            except Exception as e:
                status.update(label=f"Erreur de recherche : {e}", state="error")
                return

            if not contexts:
                status.update(label="Aucun document pertinent trouvé.", state="error")
                context_str = "Aucun contexte pertinent trouvé."
            else:
                nb_queries = 1 + (3 if cfg["use_expansion"] else 0) + (1 if cfg["use_hyde"] else 0)
                status.update(
                    label=f"{len(contexts)} extraits (sur {nb_queries} requêtes)",
                    state="complete",
                )
                context_str = "\n\n---\n\n".join(contexts)

            st.session_state.last_chunks = detailed_chunks

        # ── 3. Génération streamée ────────────────────────────────────────────
        placeholder = st.empty()
        full_response = ""
        # On passe les chunks pour étiqueter le contexte par source
        system_prompt = api.build_system_prompt(context_str, detailed_chunks)

        try:
            for token in api.stream_answer(
                system_prompt=system_prompt,
                query=prompt,
                model=cfg["model"],
                chat_history=history_for_rewrite,
            ):
                if token.startswith("ERROR:"):
                    st.error(token[6:])
                    return
                full_response += token
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")
            return

# ── 4. Parse et affiche les sources citées ────────────────────────────
        clean_response, raw_citations = api.extract_citations(full_response)

        # On enrichit les citations avec les URLs provenant de detailed_chunks
        enriched_citations = []
        for citation in raw_citations:
            url_found = ""
            for chunk in detailed_chunks:
                # Vérifie si le nom de la source correspond à la citation
                if citation in chunk["source"] or chunk["source"] in citation:
                    # Récupérer l'URL depuis les métadonnées du chunk
                    url_found = chunk.get("metadata", {}).get("source_url", "").strip()
                    if url_found:
                        break
            
            # Si une URL est trouvée, on la formate en lien Markdown cliquable
            if url_found:
                enriched_citations.append(f"**{citation}** — [Aller au document]({url_found})")
            else:
                enriched_citations.append(citation)

        # Remplacer la réponse brute par la version sans balises dans le chat
        if enriched_citations:
            placeholder.markdown(clean_response)

        _render_sources(enriched_citations)

        # ── 5. Sauvegarde ─────────────────────────────────────────────────────
        st.session_state.messages.append({
            "role": "assistant",
            "content": clean_response,
            "citations": enriched_citations, # On sauvegarde la version enrichie pour l'historique !
        })