from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from app.utils.structure_process import extract_json_structure

utils_router = APIRouter(prefix="/api/utils", tags=["utils"])


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
