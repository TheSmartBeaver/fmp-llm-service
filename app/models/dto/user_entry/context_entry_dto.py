from pydantic import BaseModel


class ContextEntryDto(BaseModel):
    course: str # Do we know in which course the flashcards will be used
    topic_path: str # Do we know in which topic the flashcards will be used
    fc_to_modify: str # Do we know if we have to modify existing flashcard