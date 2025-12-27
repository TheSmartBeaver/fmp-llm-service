from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID


class SearchSimilarRequest(BaseModel):
    text: str
    top_n: int = Field(default=5, ge=1, le=100, description="Number of similar templates to return")
    app_user_sku: UUID = Field(description="User SKU to filter templates")
    category_quotas: Optional[Dict[str, int]] = Field(
        default=None,
        description="Optional category quotas (e.g., {'Basic': 3, 'Advanced': 5}). "
                    "Remaining quota will be: top_n - sum(quotas)"
    )
    include_full_data: bool = Field(
        default=False,
        description="If True, includes SKU and Template fields in the response"
    )


class SimilarCardTemplate(BaseModel):
    sku: Optional[UUID] = None
    path: str
    template: Optional[str] = None
    full_semantic_representation: str
    short_semantic_representation: str
    similarity_score: float = Field(description="Cosine similarity score (0-1)")


class SearchSimilarResponse(BaseModel):
    results: List[SimilarCardTemplate]
    query_text: str
    total_found: int
