from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.models.dto.user_entry.user_entry_dto import UserEntryDto


class CoursePlanModificationEntryDto(BaseModel):
    """
    Requête de modification partielle d'un plan de cours.

    Le LLM ne produit que des opérations de patch ciblées sur les blocs listés ;
    la fusion et le respect des verrous ("validated": true) sont appliqués côté
    serveur.
    """

    plan_json: dict = Field(
        description='Plan de cours actuel ({"sections": [...]}, IDs "sX"/"sX.bY" attribués par le serveur)'
    )
    target_block_ids: List[str] = Field(
        default_factory=list,
        description="IDs des blocs visés par la modification (sélection visuelle côté client). Vide = laisser le LLM cibler selon l'instruction."
    )
    modification_instructions: str = Field(
        description="Instruction libre de modification à appliquer aux blocs ciblés"
    )
    user_entry: Optional[UserEntryDto] = Field(
        default=None,
        description="Données source optionnelles (nouvelles notes, nouveaux médias) à intégrer"
    )
    llm_config: Optional[LLMConfigDto] = None
