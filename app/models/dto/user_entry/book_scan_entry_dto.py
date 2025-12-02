from pydantic import BaseModel


class BookScanEntryDto(BaseModel):
    order: int # Order of the entry in the user input (AI aggregator)
    raw_data: str
    scan_screenshot: list[int] # In case raw_data is too complex to extract text correctly