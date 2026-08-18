#chatbot_utils/Chat.py

import re
import streamlit as st
from plugins import wrapper_API as api
import os
from utility.session_state_central_rh import SK

CONTEXT_SIZE = int(os.environ.get("CONTEXT_SIZE", 22000))
DEFAULT_LLM = os.environ.get("DEFAULT_LLM", "gemma4:e4b")


def _render_sources(citations: list[str]) -> None:
    if not citations:
        return
    with st.expander(f"📚 Sources citées ({len(citations)})", expanded=False):
        for src in citations:
            st.markdown(f"- 📄 {src}")


def render_chat(cfg: dict) -> None:
    # ── Historique affiché ────────────────────────────────────────────────────
    for msg in st.session_state[SK.MESSAGES]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                _render_sources(msg["citations"])

    if not (prompt := st.chat_input("Posez votre question ici")):
        return

    st.session_state[SK.MESSAGES].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        # ── 1. Réécriture contextuelle ────────────────────────────────────────
        history_for_rewrite = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state[SK.MESSAGES][:-1]
        ]
        try:
            standalone_query = api.rewrite_query(
                query=prompt,
                model=cfg["model"],
                context_size=CONTEXT_SIZE,
                chat_history=history_for_rewrite,
            )
        except Exception as e:
            st.error(f"Erreur lors de la réécriture : {e}")
            return

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
                    context_size=CONTEXT_SIZE,
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

            st.session_state[SK.LAST_CHUNKS] = detailed_chunks

        # ── 3. Génération streamée ────────────────────────────────────────────
        placeholder = st.empty()
        full_response = ""
        system_prompt = api.build_system_prompt(context_str, detailed_chunks)

        try:
            for token in api.stream_answer(
                system_prompt=system_prompt,
                query=prompt,
                model=cfg["model"],
                context_size=CONTEXT_SIZE,
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

        enriched_citations = []
        for citation in raw_citations:
            url_found = ""
            for chunk in detailed_chunks:
                if citation in chunk["source"] or chunk["source"] in citation:
                    url_found = chunk.get("metadata", {}).get("source_url", "").strip()
                    if url_found:
                        break
            if url_found:
                enriched_citations.append(f"**{citation}** — [Aller au document]({url_found})")
            else:
                enriched_citations.append(citation)

        if enriched_citations:
            placeholder.markdown(clean_response)

        _render_sources(enriched_citations)

        # ── 5. Sauvegarde ─────────────────────────────────────────────────────
        st.session_state[SK.MESSAGES].append({
            "role": "assistant",
            "content": clean_response,
            "citations": enriched_citations,
        })