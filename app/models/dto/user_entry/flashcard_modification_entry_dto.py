from pydantic import BaseModel


class FlashcardModificationEntryDto(BaseModel):
    flashcard_json: str  # JSON de la carte mentale à modifier (string)
    modification_instructions: str  # Instructions de modification (string)
