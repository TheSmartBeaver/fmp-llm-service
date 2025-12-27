import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.dto.embedding.simple_text_dto import SimpleTextDto
from app.models.dto.embedding.search_similar_dto import (
    SearchSimilarRequest,
    SearchSimilarResponse,
    SimilarCardTemplate
)
from app.database import get_db
from app.utils.template_search import fetch_similar_templates
from sentence_transformers import SentenceTransformer
import numpy as np

embedding_router = APIRouter(prefix="/embedding")

# Charger le modèle UNE SEULE FOIS (important)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

@embedding_router.post("/generate")
async def generate(request: SimpleTextDto):
    embedding = model.encode(
        request.text,
        normalize_embeddings=True  # recommandé pour cosine similarity
    )

    return {
        "id": str(uuid.uuid4()),
        "embedding": embedding.tolist(),
        "dim": len(embedding)
    }


@embedding_router.post("/search-similar", response_model=SearchSimilarResponse)
async def search_similar(request: SearchSimilarRequest, db: Session = Depends(get_db)):
    """
    Recherche les CardTemplates dont l'embedding est le plus proche du texte fourni.
    Utilise la similarité cosinus (via l'opérateur <=> de pgvector).
    Supporte les quotas par catégorie pour contrôler la distribution des templates.
    """
    # 1. Générer l'embedding du texte de recherche
    query_embedding = model.encode(
        request.text,
        normalize_embeddings=True
    ).tolist()

    # 2. Récupérer les templates similaires avec fetch_similar_templates
    templates = fetch_similar_templates(
        db=db,
        embedding=query_embedding,
        top_k=request.top_n,
        category_quotas=request.category_quotas,
        include_full_data=request.include_full_data
    )

    # 3. Convertir les résultats en objets SimilarCardTemplate
    # La distance cosinus est dans [0, 2], on convertit en similarité [0, 1]
    # similarité = 1 - (distance / 2)
    similar_templates = [
        SimilarCardTemplate(
            sku=template.get("sku"),
            path=template["template_name"],
            template=template.get("template"),
            full_semantic_representation=template["full_description"],
            short_semantic_representation=template["short_description"],
            similarity_score=1.0 - (template["similarity_distance"] / 2.0)
        )
        for template in templates
    ]

    return SearchSimilarResponse(
        results=similar_templates,
        query_text=request.text,
        total_found=len(similar_templates)
    )
