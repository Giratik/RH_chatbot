import re
import chromadb
from chromadb.utils import embedding_functions

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from config import CHROMA_HOST, CHROMA_PORT, OLLAMA_HOST, EMBEDDING_MODEL

router = APIRouter(prefix="/link", tags=["chroma_link"])

@router.get("/make_chroma_client")
def make_chroma_client() -> chromadb.HttpClient:
    try :
        return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("make_embedding_fn")
def make_embedding_fn() -> embedding_functions.OllamaEmbeddingFunction:
    try :
        return embedding_functions.OllamaEmbeddingFunction(
        url=OLLAMA_HOST + "/api/embeddings",
        model_name=EMBEDDING_MODEL,
    )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("get_collection")
def get_collection(chroma_client: chromadb.HttpClient, collection_name: str):
    try :
        return chroma_client.get_collection(
        name=collection_name,
        embedding_function=make_embedding_fn(),
    )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("list_collections")
def list_collections(chroma_client: chromadb.HttpClient) -> list[str]:
    try :
        raw = chroma_client.list_collections()
        return [c.name if hasattr(c, "name") else c for c in raw]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))