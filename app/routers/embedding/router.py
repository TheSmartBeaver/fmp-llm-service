import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import literal_column, text
from app.models.dto.embedding.simple_text_dto import SimpleTextDto
from app.models.dto.embedding.search_similar_dto import (
    SearchSimilarRequest,
    SearchSimilarResponse,
    SimilarCardTemplate
)
from app.models.db.fmp_models import CardTemplates
from app.database import get_db
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
    """
    # 1. Générer l'embedding du texte de recherche
    query_embedding = model.encode(
        request.text,
        normalize_embeddings=True
    ).tolist()

    # 2. Convertir l'embedding en format compatible avec PostgreSQL
    # Pour pgvector, on doit formater comme un string: '[0.1, 0.2, 0.3, ...]'

    embedding_str = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"

    # Utiliser SQLAlchemy ORM avec l'opérateur pgvector <=> (cosine distance)
    # literal_column permet de créer une expression SQL brute qui sera injectée telle quelle
    distance_expr = literal_column(f'"Embedding" <=> \'{embedding_str}\'::vector')

    # 4. Requête avec l'ORM SQLAlchemy
    query = (
        db.query(
            CardTemplates.SKU,
            CardTemplates.Path,
            CardTemplates.Template,
            CardTemplates.FullSemanticRepresentation,
            CardTemplates.ShortSemanticRepresentation,
            distance_expr.label('distance')
        )
        .filter(CardTemplates.Embedding.isnot(None))
        .filter(CardTemplates.IsEnabled == True)
        .order_by(distance_expr)
        .limit(request.top_n)
    )

    result = query.all()

    # 5. Convertir les résultats en objets SimilarCardTemplate
    # La distance cosinus est dans [0, 2], on convertit en similarité [0, 1]
    # similarité = 1 - (distance / 2)
    similar_templates = [
        SimilarCardTemplate(
            sku=row.SKU,
            path=row.Path,
            template=row.Template,
            full_semantic_representation=row.FullSemanticRepresentation,
            short_semantic_representation=row.ShortSemanticRepresentation,
            similarity_score=1.0 - (row.distance / 2.0)  # Convertir distance en similarité
        )
        for row in result
    ]

    return SearchSimilarResponse(
        results=similar_templates,
        query_text=request.text,
        total_found=len(similar_templates)
    )
