from pydantic import BaseModel


class SimpleTextDto(BaseModel):
    text: str