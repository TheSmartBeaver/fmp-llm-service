import os
import shutil
import subprocess
from typing import List, Tuple

# Limite dure de l'API Whisper d'OpenAI
WHISPER_MAX_BYTES = 25 * 1024 * 1024

# Durée des chunks quand le découpage est nécessaire.
# 20 min à 32 kbps ≈ 4.8 Mo, très en dessous de la limite Whisper.
CHUNK_SECONDS = 20 * 60


class FfmpegNotAvailableError(RuntimeError):
    """ffmpeg n'est pas installé sur le serveur."""


class AudioDecodeError(ValueError):
    """ffmpeg n'a pas réussi à décoder le fichier audio."""


def _run_ffmpeg(args: List[str]) -> None:
    if shutil.which("ffmpeg") is None:
        raise FfmpegNotAvailableError(
            "ffmpeg est requis pour traiter les fichiers de plus de 25 Mo"
        )
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AudioDecodeError(result.stderr.strip() or "échec du décodage ffmpeg")


def compress_to_mp3(src_path: str, dst_path: str, bitrate: str = "64k") -> None:
    """
    Transcode en mp3 mono 16 kHz. Whisper travaille en interne à 16 kHz mono :
    cette compression ne dégrade pas la qualité de transcription et les
    timecodes restent exacts puisque la durée est inchangée.
    """
    _run_ffmpeg([
        "-i", src_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-b:a", bitrate,
        dst_path,
    ])


def split_to_chunks(src_path: str, out_dir: str, segment_seconds: int = CHUNK_SECONDS) -> List[str]:
    """
    Découpe en chunks mp3 mono 16 kHz 32 kbps de segment_seconds chacun.
    Le ré-encodage (plutôt que -c copy) garantit des frontières exactement
    à segment_seconds, ce qui permet de calculer les offsets sans ffprobe.
    """
    pattern = os.path.join(out_dir, "chunk_%04d.mp3")
    _run_ffmpeg([
        "-i", src_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-b:a", "32k",
        "-f", "segment",
        "-segment_time", str(segment_seconds),
        "-reset_timestamps", "1",
        pattern,
    ])
    chunks = sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith("chunk_") and f.endswith(".mp3")
    )
    if not chunks:
        raise AudioDecodeError("le découpage n'a produit aucun chunk")
    return chunks


def prepare_for_whisper(src_path: str, workdir: str) -> List[Tuple[str, float]]:
    """
    Prépare un fichier audio pour l'API Whisper (limite 25 Mo).

    Retourne une liste de (chemin, offset_secondes) :
    - fichier déjà sous la limite → [(original, 0.0)]
    - sinon compression mp3 mono 16 kHz 64 kbps → [(mp3, 0.0)] si ça suffit
      (couvre ~53 min d'audio)
    - sinon découpage en chunks de CHUNK_SECONDS à 32 kbps, avec offsets
      cumulés pour recaler les timecodes
    """
    if os.path.getsize(src_path) <= WHISPER_MAX_BYTES:
        return [(src_path, 0.0)]

    compressed_path = os.path.join(workdir, "compressed.mp3")
    compress_to_mp3(src_path, compressed_path)
    if os.path.getsize(compressed_path) <= WHISPER_MAX_BYTES:
        return [(compressed_path, 0.0)]

    chunk_dir = os.path.join(workdir, "chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    chunks = split_to_chunks(src_path, chunk_dir)
    return [(path, float(i * CHUNK_SECONDS)) for i, path in enumerate(chunks)]
