class ImgEntryDto:
    order: int # Order of the entry in the user input (AI aggregator)
    # raw_data: list[int] # Not needed, we just need the image description
    img_description: str

    def __init__(self, raw_data: list[int], img_description: str):
        # self.raw_data = raw_data
        self.img_description = img_description