from typing import Optional
from pydantic import BaseModel

from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.models.dto.user_entry.user_entry_dto import UserEntryDto


class CourseMaterialModificationEntryDto(BaseModel):
    pedagogical_json: dict
    modification_instructions: str
    user_entry: Optional[UserEntryDto] = None
    llm_config: Optional[LLMConfigDto] = None
