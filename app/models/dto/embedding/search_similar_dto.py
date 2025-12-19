from pydantic import BaseModel, Field
from typing import List
from uuid import UUID


class SearchSimilarRequest(BaseModel):
    text: str
    top_n: int = Field(default=5, ge=1, le=100, description="Number of similar templates to return")
    app_user_sku: UUID = Field(description="User SKU to filter templates")


class SimilarCardTemplate(BaseModel):
    sku: UUID
    path: str
    template: str
    full_semantic_representation: str
    short_semantic_representation: str
    similarity_score: float = Field(description="Cosine similarity score (0-1)")


class SearchSimilarResponse(BaseModel):
    results: List[SimilarCardTemplate]
    query_text: str
    total_found: int
