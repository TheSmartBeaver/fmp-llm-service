from pydantic import BaseModel

class DictionEntryDto(BaseModel):
    order: int # Order of the entry in the user input (AI aggregator)
    text_blocs: list[str]