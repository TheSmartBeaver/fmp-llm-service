from pydantic import BaseModel
from app.models.dto.user_entry.book_scan_entry_dto import BookScanEntryDto
from app.models.dto.user_entry.context_entry_dto import ContextEntryDto
from app.models.dto.user_entry.diction_entry_dto import DictionEntryDto
from app.models.dto.user_entry.img_entry_dto import ImgEntryDto
from app.models.dto.user_entry.video_entry_dto import VideoEntryDto

# TODO: Je dois réfléchir aux blocs de blocs que l'on peut créer

class UserEntryDto(BaseModel):
    context_entry: ContextEntryDto # In which context we must generate flashcards, where are flashcards going to be inserted
    book_scan_entry: list[BookScanEntryDto]
    diction_entry: list[DictionEntryDto]
    img_entry: list[ImgEntryDto]
    video_entry: list[VideoEntryDto]