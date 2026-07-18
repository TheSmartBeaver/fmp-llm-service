import os
import shutil
import tempfile
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from openai import APIError, APIStatusError
from typing import List, Optional

from app.chains.llm.openai_whisper import OpenAiWhisper, WHISPER_MODEL, merge_transcriptions
from app.models.dto.audio.transcription_dto import (
    TranscriptionGranularity,
    TranscriptionResponseDto,
)
from app.services.audio_preprocessing import (
    AudioDecodeError,
    FfmpegNotAvailableError,
    prepare_for_whisper,
)

audio_router = APIRouter(prefix="/audio")

whisper = OpenAiWhisper()

# Formats acceptés par l'API Whisper
SUPPORTED_FORMATS = {"flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"}

# Limite d'upload côté serveur. Au-delà de 25 Mo, le fichier est automatiquement
# compressé puis découpé en chunks avant l'envoi à Whisper.
MAX_UPLOAD_SIZE_BYTES = 512 * 1024 * 1024

# Fin du texte du chunk précédent passée en prompt au chunk suivant
# pour garder la cohérence aux frontières (limite Whisper: 224 tokens)
PROMPT_TAIL_CHARS = 200


@audio_router.post("/transcribe", response_model=TranscriptionResponseDto)
async def transcribe_audio(
    file: UploadFile = File(..., description="Fichier audio à transcrire (max 512 Mo)"),
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

    Les fichiers au-delà de la limite Whisper (25 Mo) sont automatiquement
    compressés en mp3 mono 16 kHz, puis découpés en chunks de 20 min si la
    compression ne suffit pas. Les timecodes sont recalés sur l'audio d'origine.

    Args:
        file: Fichier audio (flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm), 512 Mo max
        granularities: 'segment' pour les timecodes par phrase, 'word' par mot, ou les deux
        language: Code ISO-639-1. La préciser améliore la précision et la latence
        prompt: Contexte pour aider Whisper sur le vocabulaire spécifique
        temperature: Température d'échantillonnage

    Returns:
        TranscriptionResponseDto avec le texte, la langue détectée, la durée et les timecodes

    Raises:
        HTTPException 400: Format non supporté, fichier vide ou audio illisible
        HTTPException 413: Fichier au-delà de la limite d'upload de 512 Mo
        HTTPException 500: ffmpeg absent du serveur (requis au-delà de 25 Mo)
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

    with tempfile.TemporaryDirectory() as workdir:
        # Streamer l'upload sur disque pour ne pas charger les gros fichiers en RAM
        src_path = os.path.join(workdir, f"upload.{extension}")
        size = 0
        with open(src_path, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Fichier trop volumineux. Limite d'upload: {MAX_UPLOAD_SIZE_BYTES // 1024 // 1024} Mo",
                    )
                out.write(chunk)

        if size == 0:
            raise HTTPException(status_code=400, detail="Le fichier audio est vide")

        try:
            audio_parts = prepare_for_whisper(src_path, workdir)

            transcribed_parts = []
            previous_tail: Optional[str] = None
            for i, (path, offset) in enumerate(audio_parts):
                # Premier chunk: prompt utilisateur; suivants: fin du texte précédent
                chunk_prompt = prompt if i == 0 else previous_tail
                with open(path, "rb") as audio_file:
                    part = whisper.transcribe(
                        file=audio_file,
                        granularities=granularities,
                        language=language,
                        prompt=chunk_prompt,
                        temperature=temperature,
                    )
                previous_tail = part.text[-PROMPT_TAIL_CHARS:] if part.text else None
                transcribed_parts.append((part, offset))

            return merge_transcriptions(transcribed_parts)

        except FfmpegNotAvailableError as e:
            raise HTTPException(status_code=500, detail=str(e))

        except AudioDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Le fichier audio n'a pas pu être décodé. Vérifiez qu'il n'est pas corrompu et que son format correspond à son extension.",
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
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
    }
