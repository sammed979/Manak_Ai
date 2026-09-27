from fastapi import APIRouter
from app.api.v1 import auth, knowledge, products, documents, labs, graph

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(knowledge.router)
api_router.include_router(products.router)
api_router.include_router(documents.router)
api_router.include_router(labs.router)
api_router.include_router(graph.router)
