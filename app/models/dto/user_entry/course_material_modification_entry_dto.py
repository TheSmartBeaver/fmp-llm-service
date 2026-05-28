from typing import Optional
from pydantic import BaseModel

from app.models.dto.llm_config.llm_config_dto import LLMConfigDto


class CourseMaterialModificationEntryDto(BaseModel):
    pedagogical_json: dict
    modification_instructions: str
    llm_config: Optional[LLMConfigDto] = None
