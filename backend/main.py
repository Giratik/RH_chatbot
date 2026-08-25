# backend/main.py

"""
Module : Racine de l'application Backend (FastAPI)
Description : Point d'entrée principal de l'API. Initialise l'application FastAPI,
              configure les middlewares (CORS, etc.) et inclut les différents 
              routeurs (chat, files, data_analyst).
"""

from fastapi import FastAPI

from routers import rag_engine_router

app = FastAPI(title="API Chatbot")

app.include_router(rag_engine_router.router)