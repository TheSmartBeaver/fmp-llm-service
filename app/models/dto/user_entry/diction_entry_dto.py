class DictionEntryDto:
    order: int # Order of the entry in the user input (AI aggregator)
    text_blocs: list[str]

    def __init__(self, raw_data: list[str]):
        self.raw_data = raw_data