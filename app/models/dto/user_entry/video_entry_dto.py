class VideoEntryDto:
    order: int # Order of the entry in the user input (AI aggregator)
    video_url: str
    video_description: str
    video_start_time: str

    def __init__(self, video_url: str, video_description: str, video_start_time: str):
        self.video_url = video_url
        self.video_start_time = video_start_time
        self.video_description = video_description