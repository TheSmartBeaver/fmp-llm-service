from pydantic import BaseModel

from app.models.dto.user_entry.context_entry_dto import ContextEntryDto


class PedagogicalContextEntryDto(BaseModel):
    context: ContextEntryDto
    pedagogical_json: str  # JSON pédagogique sous forme de string
