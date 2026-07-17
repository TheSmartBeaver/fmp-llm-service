from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class TranscriptionGranularity(str, Enum):
    """Granularité des timecodes retournés par Whisper."""
    SEGMENT = "segment"
    WORD = "word"


class TranscriptionWordDto(BaseModel):
    """Un mot isolé avec son timecode."""
    word: str
    start: float
    end: float


class TranscriptionSegmentDto(BaseModel):
    """Un segment de phrase avec son timecode et ses métriques de confiance."""
    id: int
    start: float
    end: float
    text: str
    avg_logprob: Optional[float] = None
    no_speech_prob: Optional[float] = None
    compression_ratio: Optional[float] = None


class TranscriptionResponseDto(BaseModel):
    """Réponse contenant la transcription et ses timecodes."""
    success: bool
    text: str
    language: str
    duration: Optional[float] = None
    segments: Optional[List[TranscriptionSegmentDto]] = None
    words: Optional[List[TranscriptionWordDto]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "text": "La photosynthèse est le processus par lequel les plantes vertes utilisent la lumière du soleil.",
                "language": "french",
                "duration": 5.62,
                "segments": [
                    {
                        "id": 0,
                        "start": 0.0,
                        "end": 5.62,
                        "text": " La photosynthèse est le processus par lequel les plantes vertes utilisent la lumière du soleil.",
                        "avg_logprob": -0.21,
                        "no_speech_prob": 0.01,
                        "compression_ratio": 1.32
                    }
                ],
                "words": None
            }
        }
