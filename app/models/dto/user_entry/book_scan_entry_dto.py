class BookScanEntryDto:
    order: int # Order of the entry in the user input (AI aggregator)
    raw_data: str
    scan_screenshot: list[int] # In case raw_data is too complex to extract text correctly

    def __init__(self, raw_data: str, scan_screenshot: list[int]):
        self.raw_data = raw_data
        self.scan_screenshot = scan_screenshot