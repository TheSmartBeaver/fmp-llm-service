from pydantic import BaseModel

class VideoEntryDto(BaseModel):
    order: int # Order of the entry in the user input (AI aggregator)
    video_url: str
    video_description: str
    video_start_time: str