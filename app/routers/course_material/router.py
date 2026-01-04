from fastapi import APIRouter, Header, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import uuid
from celery.result import AsyncResult

from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.workers.tasks import generate_course_material_task
from app.workers.celery_app import celery
from app.chains.llm.open_ai_gpt5_mini_llm import OpenAiGPT5MiniLlm
from app.chains.course_material_generator import CourseMaterialGenerator
from app.chains.course_material_generator_v2 import CourseMaterialGeneratorV2
from app.database import get_db


course_material_router = APIRouter(prefix="/course_material")

# Load embedding model and LLM
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer(MODEL_NAME)
openai_llm = OpenAiGPT5MiniLlm().get_llm()


class CourseMaterialTaskResponse(BaseModel):
    """Réponse contenant l'ID de la tâche Celery"""
    task_id: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending"
            }
        }


class CourseMaterialResponse(BaseModel):
    """Réponse contenant les supports de cours générés"""
    success: bool
    supports: list
    templates_used: int
    prompt: str
    pedagogical_json: dict = None
    destination_mappings: dict = None
    json_paths_with_variables: list = None
    path_groups: list = None
    group_jsons_list: list = None
    group_jsons_map: dict = None
    resolved_jsons_map: dict = None
    path_to_value_map: dict = None
    final_resolved_jsons_map: dict = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "supports": [],
                "templates_used": 15,
                "prompt": "Génère des supports de cours...",
                "pedagogical_json": {},
                "destination_mappings": {},
                "json_paths_with_variables": [],
                "path_groups": [],
                "group_jsons_map": {},
                "resolved_jsons_map": {},
                "path_to_value_map": {},
                "final_resolved_jsons_map": {}
            }
        }


@course_material_router.post("/generate_CELERY", response_model=CourseMaterialTaskResponse)
async def generate_course_material(
    request: UserEntryDto,
    auth_uid: str = Header(..., alias="X-Auth-Uid")
):
    """
    Lance une génération asynchrone de support de cours via Celery.

    Args:
        request: UserEntryDto contenant le contexte, le contenu textuel et les médias
        auth_uid: AuthentUid de l'utilisateur pour envoyer les notifications FCM

    Returns:
        CourseMaterialTaskResponse avec l'ID de la tâche Celery

    Note:
        Une notification FCM sera envoyée aux appareils actifs de l'utilisateur une fois la génération terminée.
    """
    # Générer un ID unique pour cette tâche
    task_id = str(uuid.uuid4())

    # Lancer la tâche Celery de manière asynchrone avec l'auth_uid
    generate_course_material_task.apply_async(
        args=[task_id, request.model_dump(), auth_uid],
        task_id=task_id
    )

    return CourseMaterialTaskResponse(
        task_id=task_id,
        status="pending"
    )


@course_material_router.post("/generate", response_model=CourseMaterialResponse)
async def generate_course_material_sync(
    request: UserEntryDto,
    db: Session = Depends(get_db),
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
    top_k: int = 15
):
    """
    Génère un support de cours de manière synchrone (sans Celery).

    Args:
        request: UserEntryDto contenant le contexte, le contenu textuel et les médias
        db: Session de base de données
        auth_uid: AuthentUid de l'utilisateur (pour compatibilité future)
        top_k: Nombre de templates à utiliser (par défaut: 15)

    Returns:
        CourseMaterialResponse avec les supports générés

    Note:
        Cette version est synchrone et retourne directement les résultats.
        Pour une version asynchrone avec notifications FCM, utilisez /generate_CELERY
    """
    import asyncio

    # Create course material generator
    generator = CourseMaterialGenerator(
        db_session=db,
        llm=openai_llm,
        embedding_model=embedding_model
    )

    # Étape 1: Agréger le contenu
    aggregated_content = generator._aggregate_content(request)

    # Étape 2: Générer les paires informations-format intermédiaires
    info_format_pairs, info_format_prompt = generator._generate_info_format_pairs(
        aggregated_content,
        request.context_entry
    )

    # Étape 3 & 4: Pour chaque paire, récupérer les templates et générer le support EN PARALLÈLE
    all_supports = []
    generation_prompts = []

    # Créer une liste de coroutines pour l'exécution parallèle
    tasks = []
    for info_format_pair in info_format_pairs:
        # Calculer l'embedding pour cette paire
        pair_text = f"{info_format_pair['objectif']} {info_format_pair['texte_associe']} {info_format_pair['format']}"
        embedding = generator._generate_embedding(pair_text)

        # Récupérer les templates pertinents pour cette paire
        templates = generator._fetch_similar_templates(embedding, top_k, { "layouts/": 3, "text/": 5}, True)

        # Créer une tâche asynchrone pour générer le support
        tasks.append(generator._generate_single_support_from_info_format_async(
            info_format_pair,
            templates,
            aggregated_content
        ))

    # Exécuter toutes les tâches en parallèle avec asyncio.gather (compatible avec FastAPI)
    results = await asyncio.gather(*tasks)

    # Extraire les résultats
    for support, gen_prompt in results:
        all_supports.append(support)
        generation_prompts.append(gen_prompt)

    # Préparer le prompt complet pour le retour
    full_prompt = f"=== PROMPT DE GÉNÉRATION DES PAIRES INFORMATIONS-FORMAT ===\n{info_format_prompt}\n\n=== PROMPTS DE GÉNÉRATION DES SUPPORTS ===\n" + "\n\n---\n\n".join(generation_prompts)

    # Étape 5: Valider le JSON de tous les supports
    validated_json = generator._validate_json(all_supports)

    return CourseMaterialResponse(
        success=True,
        supports=validated_json,
        templates_used=top_k,
        prompt=full_prompt
    )


@course_material_router.get("/result/{task_id}")
async def get_course_material_result(task_id: str):
    """
    Récupère le résultat d'une tâche de génération de supports de cours via son task_id.

    Args:
        task_id: ID unique de la tâche Celery

    Returns:
        - Si PENDING: {"status": "PENDING", "task_id": "..."}
        - Si SUCCESS: {"status": "SUCCESS", "result": {...}}
        - Si FAILURE: {"status": "FAILURE", "error": "..."}

    Raises:
        HTTPException 404: Si la tâche n'existe pas
        HTTPException 500: Si une erreur interne se produit
    """
    try:
        # Récupérer le résultat de la tâche depuis Celery
        task_result = AsyncResult(task_id, app=celery)

        # Debug logging
        print(f"🔍 Task {task_id} - State: {task_result.state}")
        print(f"🔍 Task {task_id} - Ready: {task_result.ready()}")
        print(f"🔍 Task {task_id} - Successful: {task_result.successful() if task_result.ready() else 'N/A'}")

        if task_result.state == "PENDING":
            return {
                "status": "PENDING",
                "task_id": task_id,
                "message": "La génération est en cours..."
            }

        elif task_result.state == "SUCCESS":
            result = task_result.result
            return {
                "status": "SUCCESS",
                "task_id": task_id,
                "result": result
            }

        elif task_result.state == "FAILURE":
            return {
                "status": "FAILURE",
                "task_id": task_id,
                "error": str(task_result.info)
            }

        else:
            # États intermédiaires (STARTED, RETRY, etc.)
            return {
                "status": task_result.state,
                "task_id": task_id,
                "message": f"État actuel: {task_result.state}"
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du résultat: {str(e)}"
        )


@course_material_router.post("/generate_v2", response_model=CourseMaterialResponse)
async def generate_course_material_v2(
    request: UserEntryDto,
    db: Session = Depends(get_db),
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
    top_k: int = 20
):
    """
    Génère un support de cours avec le CourseMaterialGeneratorV2 (utilise TemplateStructureGenerator).

    Cette version améliore la V1 en:
    - Créant d'abord un JSON pédagogique enrichi avec explications complètes et contextualisées
    - Utilisant TemplateStructureGenerator pour mapper vers des templates de manière cohérente
    - Produisant une structure globale cohérente (vs morceaux isolés)

    Args:
        request: UserEntryDto contenant le contexte, le contenu textuel et les médias
        db: Session de base de données
        auth_uid: AuthentUid de l'utilisateur (pour compatibilité future)
        top_k: Nombre de templates à utiliser (par défaut: 20)

    Returns:
        CourseMaterialResponse avec le support généré

    Note:
        Cette version est synchrone et retourne directement le résultat.
    """
    # Créer le générateur V2
    generator = CourseMaterialGeneratorV2(
        db_session=db,
        embedding_model=embedding_model
    )

    # Générer le support de cours (utiliser la version async)
    result = await generator.generate_course_material_async(
        user_entry=request,
        top_k=top_k,
        category_quotas=None
    )

    # Construire le prompt complet pour la réponse
    full_prompt = (
        f"=== ÉTAPE 1: GÉNÉRATION DU JSON PÉDAGOGIQUE ===\n"
        f"{result['prompts']['step1_pedagogical_json']}\n\n"
        f"=== ÉTAPE 2: MAPPING VERS TEMPLATES ===\n"
        f"{result['prompts']['step2_template_structure']}"
    )

    # Extraire les informations de débogage
    debug_info = result.get("debug_info", {})

    return CourseMaterialResponse(
        success=True,
        supports=[{"support": result["support"]}],  # Encapsuler dans une liste pour compatibilité
        templates_used=top_k,
        prompt=full_prompt,
        pedagogical_json=result.get("pedagogical_json"),
        destination_mappings=result.get("destination_mappings"),
        json_paths_with_variables=debug_info.get("json_paths_with_variables"),
        path_groups=debug_info.get("path_groups"),
        group_jsons_list=debug_info.get("group_jsons_list"),
        group_jsons_map=debug_info.get("group_jsons_map"),
        resolved_jsons_map=debug_info.get("resolved_jsons_map"),
        path_to_value_map=debug_info.get("path_to_value_map"),
        final_resolved_jsons_map=debug_info.get("final_resolved_jsons_map")
    )


@course_material_router.get("/health")
async def health_check():
    """
    Endpoint de santé pour vérifier que le service est opérationnel.
    """
    return {
        "status": "ok",
        "service": "course_material_generator",
        "llm_model": "gpt-5-mini"
    }
