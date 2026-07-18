import os
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from typing import Any, BinaryIO, List, Optional, Tuple

from app.models.dto.audio.transcription_dto import (
    TranscriptionGranularity,
    TranscriptionResponseDto,
    TranscriptionSegmentDto,
    TranscriptionWordDto,
)

# Seul whisper-1 supporte verbose_json et timestamp_granularities.
# Les modèles gpt-4o-transcribe ne renvoient pas de timecodes granulaires.
WHISPER_MODEL = "whisper-1"


class OpenAiWhisper:
    """
    Transcription audio via l'API Whisper d'OpenAI, avec timecodes.
    """

    def __init__(self, timeout: int = 300):
        """
        Args:
            timeout: Timeout en secondes (défaut: 300, les fichiers audio sont lents à traiter)
        """
        load_dotenv(find_dotenv())
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=timeout
        )

    def transcribe(
        self,
        file: BinaryIO,
        granularities: List[TranscriptionGranularity],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> TranscriptionResponseDto:
        """
        Transcrit un fichier audio et retourne le texte avec ses timecodes.

        Args:
            file: Fichier audio ouvert en binaire (doit avoir un attribut .name pour
                  que l'API déduise le format)
            granularities: Niveaux de timecodes voulus (segment et/ou word)
            language: Code ISO-639-1 de la langue (ex: "fr"). Si None, Whisper la détecte
            prompt: Contexte optionnel pour guider le vocabulaire (noms propres, jargon)
            temperature: 0.0 pour un résultat déterministe

        Returns:
            TranscriptionResponseDto avec le texte, la langue et les timecodes demandés
        """
        response = self.client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=file,
            response_format="verbose_json",
            timestamp_granularities=[g.value for g in granularities],
            language=language,
            prompt=prompt,
            temperature=temperature,
        )

        return self._to_dto(response, granularities)

    def _to_dto(
        self,
        response: Any,
        granularities: List[TranscriptionGranularity],
    ) -> TranscriptionResponseDto:
        """Convertit la réponse brute de l'API en DTO."""
        segments = None
        if TranscriptionGranularity.SEGMENT in granularities and response.segments:
            segments = [
                TranscriptionSegmentDto(
                    id=s.id,
                    start=s.start,
                    end=s.end,
                    text=s.text,
                    avg_logprob=s.avg_logprob,
                    no_speech_prob=s.no_speech_prob,
                    compression_ratio=s.compression_ratio,
                )
                for s in response.segments
            ]

        words = None
        if TranscriptionGranularity.WORD in granularities and response.words:
            words = [
                TranscriptionWordDto(word=w.word, start=w.start, end=w.end)
                for w in response.words
            ]

        return TranscriptionResponseDto(
            success=True,
            text=response.text,
            language=response.language,
            duration=response.duration,
            segments=segments,
            words=words,
        )


def merge_transcriptions(
    parts: List[Tuple[TranscriptionResponseDto, float]],
) -> TranscriptionResponseDto:
    """
    Fusionne les transcriptions de plusieurs chunks en décalant les timecodes.

    Args:
        parts: Liste de (transcription, offset_secondes du chunk dans l'audio complet)

    Returns:
        Une TranscriptionResponseDto unique, timecodes recalés sur l'audio d'origine
    """
    if len(parts) == 1 and parts[0][1] == 0.0:
        return parts[0][0]

    texts: List[str] = []
    segments: List[TranscriptionSegmentDto] = []
    words: List[TranscriptionWordDto] = []
    next_segment_id = 0

    for dto, offset in parts:
        if dto.text:
            texts.append(dto.text.strip())

        for s in dto.segments or []:
            segments.append(
                s.model_copy(update={
                    "id": next_segment_id,
                    "start": s.start + offset,
                    "end": s.end + offset,
                })
            )
            next_segment_id += 1

        for w in dto.words or []:
            words.append(
                w.model_copy(update={"start": w.start + offset, "end": w.end + offset})
            )

    last_dto, last_offset = parts[-1]
    duration = last_offset + last_dto.duration if last_dto.duration is not None else None

    return TranscriptionResponseDto(
        success=True,
        text=" ".join(texts),
        language=parts[0][0].language,
        duration=duration,
        segments=segments or None,
        words=words or None,
    )
