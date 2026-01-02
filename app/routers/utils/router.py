from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app.utils.structure_process import extract_json_structure
from app.chains.template_structure_generator import TemplateStructureGenerator
from app.utils.template_substitution import substitute_template_values
from app.database import get_db

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


class TemplateStructureResponse(BaseModel):
    """Response model pour la génération de structure de templates"""
    success: bool
    template_structure: Dict[str, Any]
    prompt: str


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
            category_quotas=request.category_quotas
        )

        return TemplateStructureResponse(
            success=True,
            template_structure=result["template_structure"],
            prompt=result["prompt"]
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
