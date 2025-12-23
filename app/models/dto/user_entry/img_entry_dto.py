from pydantic import BaseModel


class ImgEntryDto(BaseModel):
    order: int # Order of the entry in the user input (AI aggregator)
    # raw_data: list[int] # Not needed, we just need the image description
    img_description: str
    img_url: str