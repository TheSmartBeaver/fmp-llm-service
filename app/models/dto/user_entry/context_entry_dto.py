from pydantic import BaseModel
from typing import Optional


class ContextEntryDto(BaseModel):
    course: str # Do we know in which course the flashcards will be used
    topic_path: str # Do we know in which topic the flashcards will be used
    additional_instructions: Optional[str] = "" # Any specific instructions for flashcard generation
    fc_to_modify: str # Do we know if we have to modify existing flashcard