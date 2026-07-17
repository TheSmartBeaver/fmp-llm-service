import io
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from openai import APIError, APIStatusError
from typing import List, Optional

from app.chains.llm.openai_whisper import OpenAiWhisper, WHISPER_MODEL
from app.models.dto.audio.transcription_dto import (
    TranscriptionGranularity,
    TranscriptionResponseDto,
)

audio_router = APIRouter(prefix="/audio")

whisper = OpenAiWhisper()

# Formats acceptés par l'API Whisper
SUPPORTED_FORMATS = {"flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"}

# Limite imposée par l'API Whisper
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024


@audio_router.post("/transcribe", response_model=TranscriptionResponseDto)
async def transcribe_audio(
    file: UploadFile = File(..., description="Fichier audio à transcrire (max 25 Mo)"),
    granularities: List[TranscriptionGranularity] = Form(
        [TranscriptionGranularity.SEGMENT],
        description="Granularité des timecodes: 'segment' (phrases), 'word' (mots), ou les deux",
    ),
    language: Optional[str] = Form(
        None,
        description="Code ISO-639-1 de la langue (ex: 'fr', 'en'). Laisser vide pour détection automatique",
    ),
    prompt: Optional[str] = Form(
        None,
        description="Contexte optionnel pour guider le vocabulaire (noms propres, jargon)",
    ),
    temperature: float = Form(0.0, ge=0.0, le=1.0, description="0.0 pour un résultat déterministe"),
):
    """
    Transcrit un fichier audio via Whisper et retourne le texte avec ses timecodes.

    Args:
        file: Fichier audio (flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm), 25 Mo max
        granularities: 'segment' pour les timecodes par phrase, 'word' par mot, ou les deux
        language: Code ISO-639-1. La préciser améliore la précision et la latence
        prompt: Contexte pour aider Whisper sur le vocabulaire spécifique
        temperature: Température d'échantillonnage

    Returns:
        TranscriptionResponseDto avec le texte, la langue détectée, la durée et les timecodes

    Raises:
        HTTPException 400: Format non supporté, fichier vide ou granularité invalide
        HTTPException 413: Fichier au-delà de la limite de 25 Mo
        HTTPException 502: Erreur retournée par l'API OpenAI
    """
    extension = (file.filename or "").rsplit(".", 1)[-1].lower()
    if extension not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté: '{extension}'. Formats acceptés: {', '.join(sorted(SUPPORTED_FORMATS))}",
        )

    if not granularities:
        raise HTTPException(
            status_code=400,
            detail="Au moins une granularité doit être fournie ('segment' ou 'word')",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Le fichier audio est vide")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Fichier trop volumineux ({len(content) / 1024 / 1024:.1f} Mo). Limite Whisper: 25 Mo",
        )

    # L'API déduit le format depuis le nom du fichier, il doit donc être préservé
    audio_stream = io.BytesIO(content)
    audio_stream.name = file.filename

    try:
        return whisper.transcribe(
            file=audio_stream,
            granularities=granularities,
            language=language,
            prompt=prompt,
            temperature=temperature,
        )

    # Un audio illisible est une erreur du client, pas une panne d'OpenAI:
    # le renvoyer en 4xx évite de laisser croire que l'appel est à réessayer
    except APIStatusError as e:
        if e.status_code == 400:
            raise HTTPException(
                status_code=400,
                detail="Le fichier audio n'a pas pu être décodé. Vérifiez qu'il n'est pas corrompu et que son format correspond à son extension.",
            )
        raise HTTPException(
            status_code=502,
            detail=f"Erreur de l'API OpenAI: {str(e)}",
        )

    except APIError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur de l'API OpenAI: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la transcription: {str(e)}",
        )


@audio_router.get("/health")
async def health_check():
    """
    Endpoint de santé pour vérifier que le service est opérationnel.
    """
    return {
        "status": "ok",
        "service": "audio_transcription",
        "model": WHISPER_MODEL,
    }
