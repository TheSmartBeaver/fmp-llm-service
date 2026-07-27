"""
Générateur et éditeur de plan de cours.

Le plan est un artefact intermédiaire GROSSIER, éditable par l'utilisateur,
généré à partir des notes brutes (UserEntryDto). Il précède le pedagogical_json :

    UserEntryDto ──► plan (ce module) ──► pedagogical_json ──► HTML

Structure du plan :
{
  "sections": [
    {
      "id": "s1",
      "title": "Titre de la section",
      "blocks": [
        {
          "id": "s1.b1",
          "pedagogical_format": "format",
          "content": "Contenu du bloc",
          "validated": false
        }
      ]
    }
  ]
}

Les IDs sont attribués par le serveur (jamais par le LLM) et restent stables :
un bloc inséré reçoit un nouvel ID, on ne renumérote jamais les existants.
Les blocs "validated": true sont verrouillés — toute opération de modification
les ciblant est rejetée mécaniquement par apply_plan_operations.
"""
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.chains.utils.pedagogical_json_generator import (
    aggregate_content,
    format_media_for_prompt,
)
from app.models.dto.user_entry.user_entry_dto import UserEntryDto


# ---------------------------------------------------------------------------
# Attribution des IDs
# ---------------------------------------------------------------------------

_ID_NUM_RE = re.compile(r"(\d+)$")


def _next_index(existing_ids: List[str]) -> int:
    """Retourne le prochain index libre après le plus grand index déjà utilisé."""
    max_used = 0
    for existing in existing_ids:
        match = _ID_NUM_RE.search(existing)
        if match:
            max_used = max(max_used, int(match.group(1)))
    return max_used + 1


def assign_plan_ids(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attribue des IDs stables aux sections ("s1") et blocs ("s1.b2") qui n'en ont pas.

    Les IDs existants sont préservés tels quels ; les nouveaux éléments reçoivent
    l'index suivant le plus grand index déjà utilisé dans leur portée, de sorte
    qu'un ID supprimé n'est jamais réutilisé.
    """
    sections = plan.get("sections", [])
    section_ids = [s.get("id", "") for s in sections if s.get("id")]

    for section in sections:
        if not section.get("id"):
            section["id"] = f"s{_next_index(section_ids)}"
            section_ids.append(section["id"])

        blocks = section.get("blocks", [])
        block_ids = [b.get("id", "") for b in blocks if b.get("id")]
        for block in blocks:
            if not block.get("id"):
                block["id"] = f"{section['id']}.b{_next_index(block_ids)}"
                block_ids.append(block["id"])
            if "validated" not in block:
                block["validated"] = False

    return plan


# ---------------------------------------------------------------------------
# Génération du plan
# ---------------------------------------------------------------------------

_PLAN_SYSTEM_PROMPT = """Tu es un expert en ingénierie pédagogique.

CONTEXTE PÉDAGOGIQUE:
- Cours: {course}
- Chemin du sujet: {topic_path}
{additional_instructions_block}
MÉDIAS DISPONIBLES:
{media_description}

À partir des informations fournies à intégrer et transformer, génère un cours structuré au format JSON valide. Intègre les images, audios et vidéos si présentes. Varie les formats pour limiter la fatigue. Utilise exactement cette structure :

{{ "sections": [ {{ "title": "Titre de la section", "blocks": [ {{ "pedagogical_format": "format", "content": "Contenu du bloc" }} ] }} ] }}

Contraintes :
- Retourne uniquement le JSON.
- N'ajoute aucune métadonnée.
- Le champ "content" doit contenir le contenu réel destiné à l'apprenant. Tu es libre pour la forme de "content".
- N'hésite pas à rajouter de la granularité si cela aide à mieux comprendre.
- Ce plan est un artefact intermédiaire : chaque bloc doit rester synthétique (le développement détaillé sera généré plus tard à partir de ce plan et des notes sources).
- "pedagogical_format" décrit la forme pédagogique du bloc (ex: "narratif", "définition", "tableau comparatif", "encadré clé", "exemple", "image", "vidéo", "audio", ...). Sois créatif mais concis.
- Pour un bloc média, utilise "pedagogical_format": "image" / "vidéo" / "audio", mets l'URL dans un champ "url" et une légende dans "content". Les URLs gardent leur préfixe "//media:" intact.
- Place chaque média dans la section où il est le plus pertinent pédagogiquement, pas tous à la fin.
- 🚫 INTERDICTION ABSOLUE : NE crée PAS d'exercices, questions, QCM, quiz ou évaluations.
"""

_PLAN_USER_PROMPT = """Voici les notes de cours brutes à transformer en plan structuré :

CONTENU TEXTUEL:
{text}

Génère le JSON du plan en respectant strictement la structure et les contraintes ci-dessus."""


async def _invoke_json(prompt: ChatPromptTemplate, llm: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Invoque le LLM et parse la réponse JSON, en gérant la route Codex."""
    from app.chains.llm.universal_llm import UniversalLLM

    if isinstance(llm, UniversalLLM) and llm.use_codex_route:
        messages = prompt.format_messages(**inputs)
        response = await llm.ainvoke(messages)
        json_text = response.content if hasattr(response, "content") else str(response)
        return json.loads(json_text)

    chain = prompt | llm | JsonOutputParser()
    return await chain.ainvoke(inputs)


async def generate_course_plan(
    user_entry: UserEntryDto,
    plan_llm: Any,
) -> Tuple[Dict[str, Any], str]:
    """
    Génère le plan de cours à partir des notes brutes.

    Returns:
        Tuple (plan avec IDs attribués, prompt complet envoyé au LLM)
    """
    aggregated = aggregate_content(user_entry)
    media_description = format_media_for_prompt(aggregated["images"], aggregated["videos"])

    additional_instructions = aggregated["context"]["additional_instructions"]
    additional_instructions_block = (
        f"INSTRUCTIONS SUPPLÉMENTAIRES:\n{additional_instructions}\n"
        if additional_instructions
        else ""
    )

    prompt = ChatPromptTemplate.from_messages(
        [("system", _PLAN_SYSTEM_PROMPT), ("human", _PLAN_USER_PROMPT)]
    )

    inputs = {
        "course": aggregated["context"]["course"],
        "topic_path": aggregated["context"]["topic_path"],
        "additional_instructions_block": additional_instructions_block,
        "media_description": media_description,
        "text": aggregated["text"],
    }

    plan = await _invoke_json(prompt, plan_llm, inputs)
    plan = assign_plan_ids(plan)

    return plan, prompt.format(**inputs)


# ---------------------------------------------------------------------------
# Modification partielle du plan (patch par opérations)
# ---------------------------------------------------------------------------

_MODIFY_SYSTEM_PROMPT = """Tu es un expert en ingénierie pédagogique. Tu modifies un plan de cours existant par petites touches ciblées.

Le plan est un JSON {{"sections": [{{"id", "title", "blocks": [{{"id", "pedagogical_format", "content", "generation_instructions", ...}}]}}]}}.

Tu ne retournes JAMAIS le plan entier. Tu retournes UNIQUEMENT un JSON d'opérations de patch :

{{ "operations": [
  {{ "op": "replace", "target": "s2.b3", "block": {{ "content": "...", "generation_instructions": "..." }} }},
  {{ "op": "insert_after", "target": "s2.b3", "blocks": [ {{ "pedagogical_format": "...", "content": "..." }} ] }},
  {{ "op": "insert_before", "target": "s2.b1", "blocks": [ ... ] }},
  {{ "op": "delete", "target": "s2.b4" }},
  {{ "op": "rename_section", "target": "s2", "title": "Nouveau titre" }}
] }}

RÈGLES ABSOLUES :
- Retourne uniquement le JSON d'opérations, rien d'autre.
- "target" désigne toujours un ID existant du plan ("sX" pour rename_section, "sX.bY" pour les autres opérations).
- N'inclus JAMAIS de champ "id" ni "validated" dans les blocs que tu écris : le serveur les gère.
- Pour "replace", "block" est un PATCH PARTIEL : n'inclus que les champs à modifier. Tous les champs omis sont conservés par le serveur.
- "generation_instructions" contient les consignes de génération et de rendu du bloc (taille, placement, style, fichier exact, etc.). Si l'instruction utilisateur porte sur le rendu plutôt que sur le fond pédagogique, modifie ce champ sans réécrire inutilement "content".
- Modifie en priorité les BLOCS CIBLÉS listés ci-dessous. Tu peux insérer de nouveaux blocs autour d'eux si l'instruction le demande.
- 🚫 Ne touche à AUCUN bloc verrouillé (liste fournie ci-dessous) : aucune opération replace/delete ne doit les cibler.
- Ne génère aucune opération pour les blocs qui n'ont pas besoin de changer.
- Conserve le style synthétique du plan : chaque bloc reste concis.
- Les URLs de médias gardent leur préfixe "//media:" intact.
- 🚫 INTERDICTION ABSOLUE : NE crée PAS d'exercices, questions, QCM, quiz ou évaluations.
"""

_MODIFY_USER_PROMPT = """Voici le plan de cours actuel :

{plan_json}

BLOCS CIBLÉS PAR LA MODIFICATION : {target_block_ids}

BLOCS VERROUILLÉS (interdits de modification) : {locked_block_ids}
{source_block}
INSTRUCTION DE MODIFICATION :
{instructions}

Retourne UNIQUEMENT le JSON d'opérations."""


def _collect_locked_block_ids(plan: Dict[str, Any]) -> List[str]:
    locked = []
    for section in plan.get("sections", []):
        for block in section.get("blocks", []):
            if block.get("validated"):
                locked.append(block.get("id", ""))
    return [b for b in locked if b]


def _find_block(plan: Dict[str, Any], block_id: str):
    """Retourne (section, index du bloc) ou (None, -1) si introuvable."""
    for section in plan.get("sections", []):
        for i, block in enumerate(section.get("blocks", [])):
            if block.get("id") == block_id:
                return section, i
    return None, -1


def apply_plan_operations(
    plan: Dict[str, Any],
    operations: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Applique les opérations de patch sur le plan, en refusant mécaniquement
    toute opération visant un bloc verrouillé ("validated": true).

    Returns:
        Tuple (plan modifié, opérations appliquées, opérations rejetées avec raison)
    """
    plan = json.loads(json.dumps(plan))  # copie profonde
    applied: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    def reject(op: Dict[str, Any], reason: str):
        rejected.append({"operation": op, "reason": reason})

    for op in operations:
        op_type = op.get("op")
        target = op.get("target", "")

        if op_type == "rename_section":
            section = next(
                (s for s in plan.get("sections", []) if s.get("id") == target), None
            )
            if section is None:
                reject(op, f"Section introuvable: {target}")
                continue
            section["title"] = op.get("title", section.get("title", ""))
            applied.append(op)
            continue

        section, index = _find_block(plan, target)
        if section is None:
            reject(op, f"Bloc introuvable: {target}")
            continue

        target_block = section["blocks"][index]

        if op_type in ("replace", "delete") and target_block.get("validated"):
            reject(op, f"Bloc verrouillé (validated): {target}")
            continue

        if op_type == "replace":
            # Un replace est un patch partiel. Préserver les champs spécialisés
            # du plan détaillé (rendering, ordres, assets, instructions...) que
            # le LLM n'a aucune raison de répéter à chaque modification.
            new_block = dict(target_block)
            new_block.update(dict(op.get("block", {})))
            # L'ID et le verrou sont gérés par le serveur, jamais par le LLM
            new_block["id"] = target
            new_block["validated"] = False
            section["blocks"][index] = new_block
            applied.append(op)

        elif op_type == "delete":
            section["blocks"].pop(index)
            applied.append(op)

        elif op_type in ("insert_after", "insert_before"):
            new_blocks = [dict(b) for b in op.get("blocks", [])]
            for b in new_blocks:
                b.pop("id", None)
                b["validated"] = False
            insert_at = index + 1 if op_type == "insert_after" else index
            section["blocks"][insert_at:insert_at] = new_blocks
            applied.append(op)

        else:
            reject(op, f"Opération inconnue: {op_type}")

    # Attribuer des IDs aux blocs insérés
    plan = assign_plan_ids(plan)

    return plan, applied, rejected


async def modify_course_plan(
    plan: Dict[str, Any],
    target_block_ids: List[str],
    modification_instructions: str,
    plan_llm: Any,
    user_entry: Optional[UserEntryDto] = None,
) -> Dict[str, Any]:
    """
    Demande au LLM des opérations de patch ciblées puis les applique au plan.

    Le LLM ne produit que les opérations (économie de tokens) ; la fusion et
    l'application des verrous sont faites côté serveur.

    Returns:
        Dict: plan_json (fusionné), operations (appliquées), rejected_operations,
        modified_block_ids, prompt
    """
    plan = assign_plan_ids(json.loads(json.dumps(plan)))
    locked_ids = _collect_locked_block_ids(plan)

    source_block = ""
    if user_entry is not None:
        aggregated = aggregate_content(user_entry)
        media_description = format_media_for_prompt(aggregated["images"], aggregated["videos"])
        source_parts = []
        if aggregated["text"].strip():
            source_parts.append(f"CONTENU SOURCE (notes brutes) :\n{aggregated['text']}")
        source_parts.append(f"MÉDIAS DISPONIBLES :\n{media_description}")
        source_block = "\n" + "\n\n".join(source_parts) + "\n"

    prompt = ChatPromptTemplate.from_messages(
        [("system", _MODIFY_SYSTEM_PROMPT), ("human", _MODIFY_USER_PROMPT)]
    )

    inputs = {
        "plan_json": json.dumps(plan, ensure_ascii=False, indent=2),
        "target_block_ids": ", ".join(target_block_ids) if target_block_ids else "aucun ciblage précis — applique l'instruction là où c'est pertinent",
        "locked_block_ids": ", ".join(locked_ids) if locked_ids else "aucun",
        "source_block": source_block,
        "instructions": modification_instructions,
    }

    response = await _invoke_json(prompt, plan_llm, inputs)
    operations = response.get("operations", []) if isinstance(response, dict) else []

    merged_plan, applied, rejected = apply_plan_operations(plan, operations)

    # IDs des blocs réellement touchés (pour la mise en évidence côté client)
    modified_ids = []
    for op in applied:
        if op.get("op") in ("replace", "rename_section"):
            modified_ids.append(op.get("target"))
    # Les blocs insérés ont reçu leur ID à la fusion : on les retrouve par différence
    before_ids = {
        b.get("id")
        for s in plan.get("sections", [])
        for b in s.get("blocks", [])
    }
    for section in merged_plan.get("sections", []):
        for block in section.get("blocks", []):
            if block.get("id") not in before_ids:
                modified_ids.append(block.get("id"))

    return {
        "plan_json": merged_plan,
        "operations": applied,
        "rejected_operations": rejected,
        "modified_block_ids": modified_ids,
        "prompt": prompt.format(**inputs),
    }
