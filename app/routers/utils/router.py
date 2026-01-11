from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import httpx
from dotenv import find_dotenv, load_dotenv

from app.utils.structure_process import extract_json_structure
from app.chains.template_structure_generator import TemplateStructureGenerator
from app.utils.template_substitution import substitute_template_values
from app.database import get_db

load_dotenv(find_dotenv())

utils_router = APIRouter(prefix="/api/utils", tags=["utils"])

# Load embedding model
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer(MODEL_NAME)


class JsonStructureRequest(BaseModel):
    """Request model pour l'extraction de structure JSON"""
    data: Any  # Accepte n'importe quel type de données JSON


class JsonStructureResponse(BaseModel):
    """Response model pour l'extraction de structure JSON"""
    structure: Any


@utils_router.post("/extract-structure", response_model=JsonStructureResponse)
async def extract_structure(request: JsonStructureRequest):
    """
    Extrait la structure d'un JSON en cartographiant tous les chemins de clés.

    Cette route prend un JSON en entrée et retourne sa structure avec :
    - Les valeurs primitives remplacées par leur type ("string", "number", "boolean", "null")
    - Les arrays fusionnés pour montrer toutes les clés possibles
    - Les objets imbriqués traités récursivement

    Example:
        Request:
        {
            "data": {
                "name": "John",
                "items": [
                    {"id": 1, "type": "A"},
                    {"id": 2, "category": "B"}
                ]
            }
        }

        Response:
        {
            "structure": {
                "name": "string",
                "items": [
                    {
                        "id": "number",
                        "type": "string",
                        "category": "string"
                    }
                ]
            }
        }
    """
    structure = extract_json_structure(request.data)
    return JsonStructureResponse(structure=structure)


class TemplateStructureRequest(BaseModel):
    """Request model pour la génération de structure de templates"""
    source_json: Dict[str, Any]
    context_description: Optional[str] = ""
    top_k: Optional[int] = 20
    category_quotas: Optional[Dict[str, int]] = None
    hasRealDataRendered: Optional[bool] = False


class TemplateStructureResponse(BaseModel):
    """Response model pour la génération de structure de templates"""
    success: bool
    template_structure: Dict[str, Any]
    prompt: str
    debug_info: Optional[Dict[str, Any]] = None


@utils_router.post("/generate-template-structure", response_model=TemplateStructureResponse)
async def generate_template_structure(
    request: TemplateStructureRequest,
    db: Session = Depends(get_db)
):
    """
    Génère une structure de templates à partir d'un JSON source.

    Cette route prend un JSON de données et utilise un LLM pour le mapper
    vers une structure basée sur des templates disponibles.

    Example:
        Request:
        {
            "source_json": {
                "course_title": "Les verbes espagnols",
                "learning_objective": "Apprendre la conjugaison",
                "course_sections": [
                    {
                        "section_id": "section_1",
                        "section_title": "Présent de l'indicatif",
                        "tables": [
                            {
                                "verb_group": "Premier groupe",
                                "infinitive": "hablar",
                                "infinitive_translation": "parler",
                                "conjugation_table": [
                                    {
                                        "pronoun_es": "yo",
                                        "verb_form": "hablo",
                                        "translation_fr": "je parle"
                                    }
                                ]
                            }
                        ],
                        "tips": ["Attention aux accents"]
                    }
                ]
            },
            "context_description": "Cours d'espagnol sur la conjugaison",
            "top_k": 20,
            "category_quotas": {
                "layouts/": 5,
                "conceptual/": 3,
                "text/": 5
            }
        }

        Response:
        {
            "success": true,
            "template_structure": {
                "template_name": "layouts/vertical_column/container",
                "items": [...]
            },
            "prompt": "Le prompt envoyé au LLM..."
        }
    """
    try:
        generator = TemplateStructureGenerator(db, embedding_model)

        result = await generator.generate_template_structure(
            source_json=request.source_json,
            context_description=request.context_description,
            top_k=request.top_k,
            category_quotas=request.category_quotas,
            hasRealDataRendered=request.hasRealDataRendered
        )

        return TemplateStructureResponse(
            success=True,
            template_structure=result["template_structure"],
            prompt=result["prompt"],
            debug_info=result.get("debug_info")
        )
    except Exception as e:
        return TemplateStructureResponse(
            success=False,
            template_structure={},
            prompt=f"Error: {str(e)}"
        )


class TemplateSubstitutionRequest(BaseModel):
    """Request model pour la substitution de templates"""
    template_schema: Dict[str, Any]
    source_json: Dict[str, Any]
    remove_unsubstituted: Optional[bool] = False


class TemplateSubstitutionResponse(BaseModel):
    """Response model pour la substitution de templates"""
    success: bool
    result: Any
    error: Optional[str] = None


@utils_router.post("/substitute-template", response_model=TemplateSubstitutionResponse)
async def substitute_template(request: TemplateSubstitutionRequest):
    """
    Substitue les références {chemin} dans un schéma de templates par les valeurs du JSON source.

    Cette route prend un JSON schéma (généré par le LLM) avec des références comme {course_title}
    ou {course_sections[]section_title} et les remplace par les vraies valeurs du JSON source.

    Example:
        Request:
        {
            "template_schema": {
                "template_name": "layouts/vertical_column/container",
                "spacing": "2rem",
                "items": [
                    {
                        "template_name": "layouts/vertical_column/item",
                        "title": "{course_title}",
                        "content": {
                            "template_name": "text/sous_titre",
                            "text": "{learning_objective}"
                        }
                    },
                    {
                        "template_name": "layouts/vertical_column/item",
                        "title": "{course_sections[]section_title}",
                        "content": {
                            "template_name": "text/description",
                            "text": "{course_sections[]description}"
                        }
                    },
                    {
                        "template_name": "text/annotation",
                        "text": "{course_sections[]tables[]infinitive}"
                    }
                ]
            },
            "source_json": {
                "course_title": "Les verbes espagnols",
                "learning_objective": "Apprendre la conjugaison",
                "course_sections": [
                    {
                        "section_title": "Présent de l'indicatif",
                        "description": "Le présent exprime des actions actuelles",
                        "tables": [
                            {
                                "infinitive": "hablar"
                            },
                            {
                                "infinitive": "comer"
                            }
                        ]
                    },
                    {
                        "section_title": "Imparfait",
                        "description": "L'imparfait exprime des actions passées",
                        "tables": [
                            {
                                "infinitive": "vivir"
                            }
                        ]
                    }
                ]
            }
        }

        Response:
        {
            "success": true,
            "result": {
                "template_name": "layouts/vertical_column/container",
                "spacing": "2rem",
                "items": [
                    {
                        "template_name": "layouts/vertical_column/item",
                        "title": "Les verbes espagnols",
                        "content": {
                            "template_name": "text/sous_titre",
                            "text": "Apprendre la conjugaison"
                        }
                    },
                    [
                        {
                            "template_name": "layouts/vertical_column/item",
                            "title": "Présent de l'indicatif",
                            "content": {
                                "template_name": "text/description",
                                "text": "Le présent exprime des actions actuelles"
                            }
                        },
                        {
                            "template_name": "layouts/vertical_column/item",
                            "title": "Imparfait",
                            "content": {
                                "template_name": "text/description",
                                "text": "L'imparfait exprime des actions passées"
                            }
                        }
                    ],
                    [
                        {
                            "template_name": "text/annotation",
                            "text": "hablar"
                        },
                        {
                            "template_name": "text/annotation",
                            "text": "comer"
                        },
                        {
                            "template_name": "text/annotation",
                            "text": "vivir"
                        }
                    ]
                ]
            },
            "error": null
        }
    """
    try:
        result = substitute_template_values(
            template_structure=request.template_schema,
            source_data=request.source_json,
            remove_unsubstituted=request.remove_unsubstituted
        )

        return TemplateSubstitutionResponse(
            success=True,
            result=result,
            error=None
        )
    except Exception as e:
        return TemplateSubstitutionResponse(
            success=False,
            result={},
            error=f"Error: {str(e)}"
        )


class CodexMessage(BaseModel):
    """Message pour l'API Codex"""
    role: str
    content: str


class CodexRequest(BaseModel):
    """Request model pour GPT-5.1-codex"""
    messages: List[CodexMessage]
    model: Optional[str] = "gpt-5.1-codex"
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 2048


class CodexResponse(BaseModel):
    """Response model pour GPT-5.1-codex"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@utils_router.post("/codex", response_model=CodexResponse)
async def call_codex(request: CodexRequest):
    """
    Appelle directement GPT-5.1-codex via l'API OpenAI /v1/responses.

    Cette route utilise l'endpoint /v1/responses qui est spécifique aux modèles Codex
    et aux modèles de raisonnement (O-series), car ils ne sont pas compatibles avec
    l'endpoint standard /v1/chat/completions utilisé par LangChain.

    Example:
        Request:
        {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Python expert."
                },
                {
                    "role": "user",
                    "content": "Write a function to calculate fibonacci numbers"
                }
            ],
            "model": "gpt-5.1-codex",
            "temperature": 0.0,
            "max_tokens": 2048
        }

        Response:
        {
            "success": true,
            "response": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    ...",
            "error": null,
            "raw_response": {...}
        }
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

        # Convertir les messages en format API OpenAI
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Construire le payload pour l'API /v1/responses
        # Note: L'API /v1/responses utilise 'input' au lieu de 'messages'
        # Les modèles Codex et O-series n'acceptent ni 'max_tokens' ni 'temperature'
        payload = {
            "model": request.model,
            "input": messages_dict,
        }

        # Appel direct à l'API OpenAI /v1/responses
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", response.text)
                except:
                    pass

                return CodexResponse(
                    success=False,
                    response=None,
                    error=f"API Error {response.status_code}: {error_detail}",
                    raw_response=None
                )

            result = response.json()

            # Extraire la réponse du modèle
            # Le format peut varier selon l'endpoint, adapter si nécessaire
            response_text = None
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice:
                    response_text = choice["message"].get("content", "")
                elif "text" in choice:
                    response_text = choice["text"]

            return CodexResponse(
                success=True,
                response=response_text,
                error=None,
                raw_response=result
            )

    except httpx.TimeoutException:
        return CodexResponse(
            success=False,
            response=None,
            error="Request timeout",
            raw_response=None
        )
    except Exception as e:
        return CodexResponse(
            success=False,
            response=None,
            error=f"Error: {str(e)}",
            raw_response=None
        )


class TextDistanceRequest(BaseModel):
    """Request model pour le calcul de distance entre deux textes"""
    text1: str
    text2: str
    metric: Optional[str] = "cosine"


class TextDistanceResponse(BaseModel):
    """Response model pour le calcul de distance entre deux textes"""
    success: bool
    distance: Optional[float] = None
    similarity: Optional[float] = None
    metric: str
    error: Optional[str] = None


@utils_router.post("/text-distance", response_model=TextDistanceResponse)
async def calculate_text_distance(request: TextDistanceRequest):
    """
    Calcule la distance sémantique entre deux textes en utilisant les embeddings.

    Cette route utilise le même modèle d'embeddings (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
    que celui utilisé pour la génération de templates. Elle calcule les embeddings des deux textes
    et retourne la distance/similarité cosine entre eux.

    Métriques supportées:
    - cosine: Similarité cosine (valeur entre -1 et 1, plus proche de 1 = plus similaire)

    Example:
        Request:
        {
            "text1": "Le chat dort sur le canapé",
            "text2": "Un félin se repose sur le sofa",
            "metric": "cosine"
        }

        Response:
        {
            "success": true,
            "distance": 0.123,
            "similarity": 0.877,
            "metric": "cosine",
            "error": null
        }
    """
    try:
        # Valider la métrique
        if request.metric not in ["cosine"]:
            return TextDistanceResponse(
                success=False,
                distance=None,
                similarity=None,
                metric=request.metric,
                error=f"Metric '{request.metric}' is not supported. Supported metrics: cosine"
            )

        # Calculer les embeddings pour les deux textes
        embedding1 = embedding_model.encode([request.text1])[0]
        embedding2 = embedding_model.encode([request.text2])[0]

        # Calculer la similarité cosine
        embedding1_reshaped = embedding1.reshape(1, -1)
        embedding2_reshaped = embedding2.reshape(1, -1)
        similarity = cosine_similarity(embedding1_reshaped, embedding2_reshaped)[0][0]

        # La distance cosine est 1 - similarité
        distance = 1.0 - similarity

        return TextDistanceResponse(
            success=True,
            distance=float(distance),
            similarity=float(similarity),
            metric=request.metric,
            error=None
        )

    except Exception as e:
        return TextDistanceResponse(
            success=False,
            distance=None,
            similarity=None,
            metric=request.metric,
            error=f"Error: {str(e)}"
        )

