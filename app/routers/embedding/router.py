import uuid
from fastapi import APIRouter
from app.models.dto.embedding.simple_text_dto import SimpleTextDto
from sentence_transformers import SentenceTransformer

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
