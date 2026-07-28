# 🤖 Chatbot RH - Assistant IA pour les Ressources Humaines

Bienvenue sur le dépôt du projet **Chatbot RH**. Ce projet déploie un assistant conversationnel intelligent dédié aux problématiques des Ressources Humaines. Il utilise l'IA générative et l'architecture **RAG (Retrieval-Augmented Generation)** pour fournir des réponses précises basées sur les documents internes de l'entreprise.

---

## 🚀 Fonctionnalités principales

* **Interface Utilisateur Intuitive :** Interface web développée avec Streamlit pour une interaction fluide (chat, configuration, historique).
* **Moteur RAG (Retrieval-Augmented Generation) :** Permet d'interroger vos propres documents RH (PDF, textes, etc.) pour des réponses contextualisées.
* **Intégration d'Ollama :** Utilisation de modèles de langage locaux (LLM) de manière sécurisée et privée via l'API Ollama.
* **Gestion des Fichiers :** Upload et traitement sécurisé des documents de connaissances RH.
* **Déploiement Conteneurisé :** Déploiement facile et reproductible grâce à Docker et Docker Compose.

---

## 🏗️ Architecture du Projet

Le projet est divisé en deux parties principales : un **Frontend** (Streamlit) et un **Backend** (FastAPI).

### Diagramme de flux (Architecture)

```mermaid
flowchart TD
    %% Définition des acteurs et composants
    User([🧑‍💻 Utilisateur / RH])
    
    subgraph "Interface Utilisateur (Docker Container)"
        UI[💻 Frontend : Streamlit]
    end

    subgraph "Serveur API (Docker Container)"
        API[⚙️ Backend : FastAPI]
        RouterChat[Routeur Chat]
        RouterFiles[Routeur Fichiers]
        RouterRAG[Routeur RAG]
        RAGEngine[🧠 Moteur RAG]
    end
    
    subgraph "Services Externes / IA"
        Ollama[🤖 Serveur Ollama LLM]
        VectorDB[(🗄️ Base de Données Vectorielle)]
        FileSystem[(📁 Stockage local)]
    end

    %% Flux d'interactions
    User <-->|Pose des questions / Upload des fichiers| UI
    UI <-->|Requêtes HTTP REST| API
    
    API --> RouterChat
    API --> RouterFiles
    API --> RouterRAG
    
    RouterFiles -->|Sauvegarde les documents| FileSystem
    RouterRAG -->|Orchestre l'indexation & la recherche| RAGEngine
    RouterChat -->|Traite les requêtes de chat| RAGEngine
    
    FileSystem -.->|Fournit le texte à indexer| RAGEngine
    RAGEngine <-->|Génère des embeddings & recherche| VectorDB
    RAGEngine <-->|Génération de texte => Prompts| Ollama