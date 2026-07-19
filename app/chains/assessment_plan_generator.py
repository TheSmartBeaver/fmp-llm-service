"""
Plans et générations pour les évaluations (quiz et flashcards).

Deux niveaux de plan, réutilisant la machinerie de course_plan_generator
(IDs stables sX/sX.bY, patchs ciblés via /course_material/modify_plan_CELERY,
verrous "validated") :

1. Plans GÉNÉRAUX (kind "quiz" / "flashcards") : 1 bloc = 1 entité esquissée,
   générés depuis le pedagogical_json du support de cours.
2. Plans d'ENTITÉ (kind "quiz_question_html" / "flashcard_full_html") : plan
   de construction détaillé d'UNE question de quiz en mode HTML (slots
   question / answer_N / explanation_N) ou d'UNE flashcard full HTML
   (convention <!--ANSWER_HIDDEN--> + classe fmp-hidden).

Les CardTemplates ne voyagent dans les plans que par référence
({path, fields_usage}) ; leur HTML complet n'est fourni qu'à la génération
finale, où il est transplanté verbatim (structure et CSS conservés).
"""
import json
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate

from app.chains.course_plan_generator import assign_plan_ids, _invoke_json


ANSWER_HIDDEN_MARKER = "<!--ANSWER_HIDDEN-->"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _context_block(course_name: Optional[str], topic_path: Optional[str],
                   additional_instructions: Optional[str]) -> str:
    parts = []
    if course_name:
        parts.append(f"Cours : {course_name}")
    if topic_path:
        parts.append(f"Topic : {topic_path}")
    if additional_instructions:
        parts.append(f"INSTRUCTIONS SUPPLÉMENTAIRES : {additional_instructions}")
    return "\n".join(parts) if parts else "Aucun contexte fourni."


def _media_block(media: Optional[List[Dict[str, Any]]]) -> str:
    """Formate les fichiers joints (audio, image, vidéo...) pour un prompt."""
    if not media:
        return "Aucun média joint."
    lines = ["MÉDIAS JOINTS (URLs à préserver avec leur préfixe //media:) :"]
    for i, m in enumerate(media, 1):
        kind = m.get("media_type", "media")
        lines.append(f"  - {kind} {i}: {m.get('description', '')} (URL: {m.get('url', '')})")
    return "\n".join(lines)


def _template_refs_block(template_refs: Optional[List[Dict[str, Any]]]) -> str:
    """Formate les références de CardTemplate (path + mode d'emploi, JAMAIS le HTML)."""
    if not template_refs:
        return "Aucun template fourni."
    lines = ["CARD TEMPLATES DISPONIBLES (référence uniquement — le HTML complet sera fourni à la génération finale) :"]
    for ref in template_refs:
        lines.append(f"  - path: {ref.get('path', '')}")
        usage = ref.get("fields_usage", "")
        if usage:
            lines.append(f"    mode d'emploi: {usage}")
    return "\n".join(lines)


def _templates_full_block(templates: Optional[List[Dict[str, Any]]]) -> str:
    """Formate les CardTemplates complets pour la génération finale (transplantation)."""
    if not templates:
        return "Aucun template à transplanter."
    parts = ["CARD TEMPLATES À TRANSPLANTER (reprends leur structure HTML et leur CSS TELS QUELS, n'adapte que le contenu des champs décrits par le mode d'emploi) :"]
    for t in templates:
        parts.append(f"--- TEMPLATE path={t.get('path', '')} ---")
        usage = t.get("fields_usage", "")
        if usage:
            parts.append(f"MODE D'EMPLOI : {usage}")
        parts.append(t.get("template", ""))
    return "\n".join(parts)


def validate_full_html_marker(full_html: str) -> Optional[str]:
    """
    Vérifie la convention full HTML : le marqueur ANSWER_HIDDEN présent
    exactement une fois, en fin de document, suivi du code de masquage.

    Returns:
        None si valide, sinon un message d'erreur exploitable pour un retry.
    """
    count = full_html.count(ANSWER_HIDDEN_MARKER)
    if count == 0:
        return f"Le marqueur {ANSWER_HIDDEN_MARKER} est absent du HTML."
    if count > 1:
        return f"Le marqueur {ANSWER_HIDDEN_MARKER} apparaît {count} fois (attendu : une seule)."
    after = full_html.split(ANSWER_HIDDEN_MARKER, 1)[1].strip()
    if not after:
        return (
            f"Rien ne suit le marqueur {ANSWER_HIDDEN_MARKER} : il doit être suivi "
            "du code (ex: <style>) qui masque la classe fmp-hidden."
        )
    if "fmp-hidden" not in after:
        return (
            "Le code placé après le marqueur ne référence pas la classe fmp-hidden : "
            "c'est lui qui doit masquer les éléments de réponse."
        )
    return None


# ---------------------------------------------------------------------------
# Plans généraux (kind "quiz" / "flashcards")
# ---------------------------------------------------------------------------

_GENERAL_PLAN_SYSTEM = """Tu es un expert en ingénierie pédagogique. Tu construis le PLAN d'un ensemble de {entity_label} à partir d'un contenu de cours.

CONTEXTE :
{context_block}

{kind_rules}

Utilise exactement cette structure JSON :
{{ "kind": "{kind}", "sections": [ {{ "title": "Titre du regroupement thématique", "blocks": [ {{ "pedagogical_format": "format", "content": "Esquisse de l'entité" }} ] }} ] }}

Contraintes :
- Retourne uniquement le JSON, aucune métadonnée.
- CHAQUE BLOC = UNE ENTITÉ ({entity_singular}). Les sections ne servent qu'à regrouper par thème.
- Chaque bloc reste synthétique : c'est une esquisse, le contenu final sera généré plus tard à partir de ce plan et du contenu de cours.
- Varie les formats pour limiter la fatigue et couvrir les points clés du contenu.
- N'ajoute NI "id" NI "validated" : le serveur les gère.
- 🚫 Ne recopie pas de longues portions du contenu de cours dans les blocs.
"""

_GENERAL_PLAN_KIND_RULES = {
    "quiz": """RÈGLES POUR UN PLAN DE QUIZ :
- "pedagogical_format" décrit le type de question (ex: "QCM classique", "QCM piège", "vrai/faux", "cas pratique", ...).
- "content" esquisse la question : l'angle testé, la bonne réponse attendue, et l'idée des distracteurs.
- Couvre les points clés du contenu, du plus fondamental au plus subtil.""",
    "flashcards": """RÈGLES POUR UN PLAN DE FLASHCARDS :
- "pedagogical_format" décrit le type de carte (ex: "définition", "texte à trou", "date clé", "formule", "cause→conséquence", ...).
- "content" esquisse la carte : la question (avec son contexte, sans trop d'indices) et la réponse attendue — COURTE, UNIQUE et non ambiguë, pour une révision rapide.
- Une carte = une seule information à mémoriser.""",
}

_GENERAL_PLAN_USER = """CONTENU DE COURS (pedagogical_json) :
{pedagogical_json}
{course_plan_block}
Génère le JSON du plan en respectant strictement la structure et les contraintes ci-dessus."""


async def generate_assessment_plan(
    kind: str,
    pedagogical_json: Dict[str, Any],
    plan_llm: Any,
    course_plan_json: Optional[Dict[str, Any]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Génère le plan général d'un quiz ("quiz") ou d'un jeu de cartes ("flashcards")."""
    entity_label = "questions de quiz" if kind == "quiz" else "flashcards"
    entity_singular = "une question de quiz" if kind == "quiz" else "une flashcard"

    course_plan_block = ""
    if course_plan_json:
        course_plan_block = (
            "\nPLAN DU COURS (pour t'aligner sur sa structure) :\n"
            + json.dumps(course_plan_json, ensure_ascii=False)
            + "\n"
        )

    prompt = ChatPromptTemplate.from_messages(
        [("system", _GENERAL_PLAN_SYSTEM), ("human", _GENERAL_PLAN_USER)]
    )
    inputs = {
        "kind": kind,
        "entity_label": entity_label,
        "entity_singular": entity_singular,
        "kind_rules": _GENERAL_PLAN_KIND_RULES[kind],
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "pedagogical_json": json.dumps(pedagogical_json, ensure_ascii=False),
        "course_plan_block": course_plan_block,
    }

    plan = await _invoke_json(prompt, plan_llm, inputs)
    plan["kind"] = kind
    plan = assign_plan_ids(plan)
    return plan, prompt.format(**inputs)


# ---------------------------------------------------------------------------
# Plan d'entité : question de quiz en mode HTML
# ---------------------------------------------------------------------------

_QUESTION_PLAN_SYSTEM = """Tu es un expert en ingénierie pédagogique. Tu construis le PLAN DE CONSTRUCTION d'UNE question de quiz riche (mode HTML).

CONTEXTE :
{context_block}

{media_block}

La question finale est composée de SLOTS : un énoncé, des réponses ordonnées, des explications. Chaque slot sera rendu soit en texte simple, soit en HTML riche.

Utilise exactement cette structure JSON :
{{
  "kind": "quiz_question_html",
  "sections": [
    {{ "title": "Énoncé", "slot_group": "question",
       "blocks": [ {{ "pedagogical_format": "format", "content": "...", "rendering": "html" }} ] }},
    {{ "title": "Réponses", "slot_group": "answers",
       "blocks": [ {{ "pedagogical_format": "réponse", "content": "...", "answer_order": 1, "correct": true, "rendering": "html" }} ] }},
    {{ "title": "Explications", "slot_group": "explanations",
       "blocks": [ {{ "pedagogical_format": "explication", "content": "...", "explanation_order": 0, "rendering": "html" }} ] }}
  ]
}}

Contraintes :
- Retourne uniquement le JSON, aucune métadonnée. N'ajoute NI "id" NI "validated".
- EXACTEMENT trois sections, avec ces "slot_group" : "question", "answers", "explanations".
- Section "question" : un ou plusieurs blocs décrivant l'énoncé (texte, tableau, extrait de code, média...). Un bloc média porte "url" (préfixe //media: intact).
- Section "answers" : 2 à 4 blocs, "answer_order" séquentiel à partir de 1, EXACTEMENT un bloc avec "correct": true. Les mauvaises réponses doivent être plausibles.
- Section "explanations" : un bloc "explanation_order": 0 (explication générale) + idéalement un bloc par réponse ("explanation_order" = answer_order correspondant).
- "rendering" : PAR DÉFAUT "html" pour TOUS les slots (énoncé, réponses ET explications), afin d'obtenir un rendu riche cohérent. Ne mets "rendering": "text" QUE si les instructions supplémentaires demandent explicitement du texte simple pour un slot donné.
- Intègre les médias joints dans le slot le plus pertinent (énoncé et/ou réponses).
- "content" reste synthétique : il décrit ce que le slot contiendra, le HTML final sera généré plus tard.
"""

_QUESTION_PLAN_USER = """CONTENU DE COURS (contexte) :
{pedagogical_json}
{source_block}
Génère le JSON du plan de construction de la question."""


async def generate_quiz_question_plan(
    plan_llm: Any,
    pedagogical_json: Optional[Dict[str, Any]] = None,
    source_block: Optional[Dict[str, Any]] = None,
    media: Optional[List[Dict[str, Any]]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Génère le plan de construction d'une question de quiz en mode HTML."""
    source_txt = ""
    if source_block:
        source_txt = (
            "\nBLOC DU PLAN GÉNÉRAL À DÉVELOPPER (la question doit en découler) :\n"
            + json.dumps(source_block, ensure_ascii=False)
            + "\n"
        )

    prompt = ChatPromptTemplate.from_messages(
        [("system", _QUESTION_PLAN_SYSTEM), ("human", _QUESTION_PLAN_USER)]
    )
    inputs = {
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "media_block": _media_block(media),
        "pedagogical_json": json.dumps(pedagogical_json or {}, ensure_ascii=False),
        "source_block": source_txt,
    }

    plan = await _invoke_json(prompt, plan_llm, inputs)
    plan["kind"] = "quiz_question_html"
    plan = assign_plan_ids(plan)
    return plan, prompt.format(**inputs)


# ---------------------------------------------------------------------------
# Plan d'entité : flashcard full HTML
# ---------------------------------------------------------------------------

_CARD_PLAN_SYSTEM = """Tu es un expert en ingénierie pédagogique. Tu construis le PLAN DE CONSTRUCTION d'UNE flashcard "full HTML".

CONTEXTE :
{context_block}

{media_block}

{template_refs_block}

La carte finale sera une carte mentale responsive en un seul document HTML : la question visible, la réponse portée par des éléments de classe "fmp-hidden", et à la toute fin le commentaire {marker} suivi du code qui masque "fmp-hidden".

Utilise exactement cette structure JSON :
{{
  "kind": "flashcard_full_html",
  "sections": [
    {{ "title": "Question (visible)", "role": "visible",
       "blocks": [ {{ "pedagogical_format": "format", "content": "..." }} ] }},
    {{ "title": "Réponse (fmp-hidden)", "role": "hidden",
       "blocks": [ {{ "pedagogical_format": "format", "content": "..." }} ] }}
  ]
}}

Contraintes :
- Retourne uniquement le JSON, aucune métadonnée. N'ajoute NI "id" NI "validated".
- EXACTEMENT deux sections, avec ces "role" : "visible" puis "hidden".
- Section visible : la question, avec son contexte rappelé sans trop donner d'indices. Un bloc média porte "url" (préfixe //media: intact).
- Section hidden : la réponse — COURTE, UNIQUE, non ambiguë, révisable en quelques secondes.
- Pour utiliser un template fourni, crée un bloc {{"pedagogical_format": "template", "template_path": "<path>", "content": "consigne d'adaptation des champs"}}. Ne recopie JAMAIS de HTML de template : seule la référence par path compte, le HTML complet sera fourni à la génération finale.
- "content" reste synthétique : il décrit ce que la carte contiendra, le HTML final sera généré plus tard.
"""

_CARD_PLAN_USER = """CONTENU DE COURS (contexte) :
{pedagogical_json}
{source_block}
Génère le JSON du plan de construction de la carte."""


async def generate_flashcard_plan(
    plan_llm: Any,
    pedagogical_json: Optional[Dict[str, Any]] = None,
    source_block: Optional[Dict[str, Any]] = None,
    template_refs: Optional[List[Dict[str, Any]]] = None,
    media: Optional[List[Dict[str, Any]]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Génère le plan de construction d'une flashcard full HTML."""
    source_txt = ""
    if source_block:
        source_txt = (
            "\nBLOC DU PLAN GÉNÉRAL À DÉVELOPPER (la carte doit en découler) :\n"
            + json.dumps(source_block, ensure_ascii=False)
            + "\n"
        )

    prompt = ChatPromptTemplate.from_messages(
        [("system", _CARD_PLAN_SYSTEM), ("human", _CARD_PLAN_USER)]
    )
    inputs = {
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "media_block": _media_block(media),
        "template_refs_block": _template_refs_block(template_refs),
        "marker": ANSWER_HIDDEN_MARKER,
        "pedagogical_json": json.dumps(pedagogical_json or {}, ensure_ascii=False),
        "source_block": source_txt,
    }

    plan = await _invoke_json(prompt, plan_llm, inputs)
    plan["kind"] = "flashcard_full_html"
    if template_refs:
        plan["template_refs"] = template_refs
    plan = assign_plan_ids(plan)
    return plan, prompt.format(**inputs)


# ---------------------------------------------------------------------------
# Génération directe de questions depuis le plan général (mode texte classique)
# ---------------------------------------------------------------------------

_QUIZ_FROM_PLAN_PROMPT = """Tu es un expert en pédagogie. Génère des questions de quiz à partir du plan de quiz validé et du contenu pédagogique.

{context_block}

PLAN DE QUIZ VALIDÉ :
{plan_json}

BLOCS À GÉNÉRER (ne génère RIEN d'autre) : {target_block_ids}

CONTENU PÉDAGOGIQUE (source du détail) :
{pedagogical_json}

Pour CHAQUE bloc ciblé, génère UNE question fidèle à son esquisse (format, angle, réponse attendue).
Chaque question doit avoir entre 2 et 4 réponses possibles. Les réponses incorrectes doivent être plausibles et difficiles à distinguer de la bonne réponse.

Réponds UNIQUEMENT avec un objet JSON valide respectant exactement ce format :
{{
  "quiz_items": [
    {{
      "planBlock": "ID_DU_BLOC_DU_PLAN",
      "questionJson": {{"type": "simpleText", "version": 1, "content": "TEXTE_DE_LA_QUESTION"}},
      "answersJson": {{
        "type": "simpleText",
        "version": 1,
        "content": [
          {{"order": 1, "text": "RÉPONSE_1"}},
          {{"order": 2, "text": "RÉPONSE_2"}}
        ]
      }},
      "explanationJson": {{
        "type": "simpleText",
        "version": 1,
        "content": [
          {{"order": 0, "text": "EXPLICATION_GÉNÉRALE"}},
          {{"order": 1, "text": "EXPLICATION_RÉPONSE_1"}},
          {{"order": 2, "text": "EXPLICATION_RÉPONSE_2"}}
        ]
      }},
      "correctAnswerOrder": 1
    }}
  ]
}}

Règles :
- "planBlock" reprend l'ID exact du bloc du plan dont la question découle
- correctAnswerOrder correspond à l'order de la bonne réponse dans answersJson.content
- explanationJson.content doit avoir order 0 (explication générale) + un order par réponse
- Ne génère que du JSON, aucun texte autour"""


async def generate_quiz_from_plan(
    plan_json: Dict[str, Any],
    target_block_ids: List[str],
    pedagogical_json: Dict[str, Any],
    llm: Any,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """Génère les questions (mode texte classique) des blocs ciblés du plan général."""
    prompt = ChatPromptTemplate.from_messages([("human", _QUIZ_FROM_PLAN_PROMPT)])
    inputs = {
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "plan_json": json.dumps(plan_json, ensure_ascii=False),
        "target_block_ids": ", ".join(target_block_ids),
        "pedagogical_json": json.dumps(pedagogical_json, ensure_ascii=False),
    }
    result = await _invoke_json(prompt, llm, inputs)
    items = result.get("quiz_items", []) if isinstance(result, dict) else []
    return items, prompt.format(**inputs)


# ---------------------------------------------------------------------------
# Génération finale : flashcard(s) full HTML
# ---------------------------------------------------------------------------

_CARD_HTML_BASE_RULES = """RÈGLES DE LA CARTE (STRICTES) :
- Carte mentale responsive, SANS javascript, avec CSS inline, police moyenne.
- La carte prend l'espace en hauteur et n'utilise PAS de branches.
- La réponse est COURTE pour une révision rapide, UNIQUE, et on ne peut pas répondre autre chose.
- Rappelle le contexte dans la question sans trop donner d'indices.
- Ajoute une classe "fmp-hidden" sur TOUS les éléments à cacher, pour qu'on ne voie que la question, pas la réponse.
- Place le commentaire {marker} à la TOUTE FIN du HTML. C'est APRÈS ce commentaire que tu définis le code (ex: <style>) qui masque "fmp-hidden".
- Les URLs de médias : retire le préfixe "//media:" dans les attributs src.
- Retourne uniquement le JSON demandé, aucun texte autour."""


_CARDS_FROM_PLAN_PROMPT = """Tu es un expert en création de flashcards HTML pédagogiques.

{context_block}

PLAN DE FLASHCARDS VALIDÉ :
{plan_json}

BLOCS À GÉNÉRER (ne génère RIEN d'autre) : {target_block_ids}

CONTENU PÉDAGOGIQUE (source du détail) :
{pedagogical_json}

{templates_block}

Pour CHAQUE bloc ciblé, génère UNE carte full HTML fidèle à son esquisse.

""" + _CARD_HTML_BASE_RULES + """

Format de sortie :
{{ "cards": [ {{ "plan_block": "ID_DU_BLOC", "full_html": "<div>...</div>{marker}<style>.fmp-hidden{{visibility:hidden}}</style>" }} ] }}"""


_CARD_HTML_FROM_ENTITY_PLAN_PROMPT = """Tu es un expert en création de flashcards HTML pédagogiques.

{context_block}

PLAN DE CONSTRUCTION VALIDÉ DE LA CARTE (suis-le STRICTEMENT — section "visible" = question, section "hidden" = réponse à masquer) :
{plan_json}

CONTENU PÉDAGOGIQUE (source du détail) :
{pedagogical_json}

{templates_block}

Génère LA carte full HTML décrite par ce plan. Chaque bloc "template" du plan doit être rendu en transplantant le template correspondant (structure et CSS repris tels quels, seuls les champs décrits par le mode d'emploi sont remplis).

""" + _CARD_HTML_BASE_RULES + """

Format de sortie :
{{ "cards": [ {{ "plan_block": "root", "full_html": "<div>...</div>{marker}<style>.fmp-hidden{{visibility:hidden}}</style>" }} ] }}"""


async def _generate_cards_html(
    prompt_template: str,
    inputs: Dict[str, Any],
    llm: Any,
) -> Tuple[List[Dict[str, Any]], str]:
    """Génère des cartes full HTML et valide la convention du marqueur (1 retry)."""
    prompt = ChatPromptTemplate.from_messages([("human", prompt_template)])
    result = await _invoke_json(prompt, llm, inputs)
    cards = result.get("cards", []) if isinstance(result, dict) else []

    errors = []
    for card in cards:
        error = validate_full_html_marker(card.get("full_html", ""))
        if error:
            errors.append(f"[{card.get('plan_block', '?')}] {error}")

    if errors:
        retry_template = prompt_template + (
            "\n\nATTENTION — ta précédente réponse était invalide :\n"
            + "\n".join(errors)
            + "\nCorrige ces problèmes et régénère TOUTES les cartes."
        )
        retry_prompt = ChatPromptTemplate.from_messages([("human", retry_template)])
        result = await _invoke_json(retry_prompt, llm, inputs)
        cards = result.get("cards", []) if isinstance(result, dict) else []
        remaining = [
            e for card in cards
            if (e := validate_full_html_marker(card.get("full_html", "")))
        ]
        if remaining:
            raise ValueError(
                "Cartes full HTML invalides après retry : " + " ; ".join(remaining)
            )

    return cards, prompt.format(**inputs)


async def generate_flashcards_from_plan(
    plan_json: Dict[str, Any],
    target_block_ids: List[str],
    pedagogical_json: Dict[str, Any],
    llm: Any,
    templates: Optional[List[Dict[str, Any]]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """Génère les cartes full HTML des blocs ciblés du plan général."""
    inputs = {
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "plan_json": json.dumps(plan_json, ensure_ascii=False),
        "target_block_ids": ", ".join(target_block_ids),
        "pedagogical_json": json.dumps(pedagogical_json, ensure_ascii=False),
        "templates_block": _templates_full_block(templates),
        "marker": ANSWER_HIDDEN_MARKER,
    }
    return await _generate_cards_html(_CARDS_FROM_PLAN_PROMPT, inputs, llm)


async def generate_flashcard_html_from_plan(
    entity_plan_json: Dict[str, Any],
    llm: Any,
    templates: Optional[List[Dict[str, Any]]] = None,
    pedagogical_json: Optional[Dict[str, Any]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """Génère LA carte full HTML décrite par un plan d'entité."""
    inputs = {
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "plan_json": json.dumps(entity_plan_json, ensure_ascii=False),
        "pedagogical_json": json.dumps(pedagogical_json or {}, ensure_ascii=False),
        "templates_block": _templates_full_block(templates),
        "marker": ANSWER_HIDDEN_MARKER,
    }
    return await _generate_cards_html(_CARD_HTML_FROM_ENTITY_PLAN_PROMPT, inputs, llm)


# ---------------------------------------------------------------------------
# Génération finale : question de quiz HTML (par slots)
# ---------------------------------------------------------------------------

_QUESTION_HTML_PROMPT = """Tu es un expert en création de contenu HTML pédagogique. Tu génères UNE question de quiz riche à partir de son plan de construction validé.

{context_block}

PLAN DE CONSTRUCTION VALIDÉ (suis-le STRICTEMENT — sections "question" / "answers" / "explanations") :
{plan_json}

CONTENU PÉDAGOGIQUE (source du détail) :
{pedagogical_json}

La question est composée de SLOTS : "question", "answer_1..N", "explanation_0..N". Chaque slot du plan a un "rendering" : "html" (bloc riche) ou "text" (texte simple).

Réponds UNIQUEMENT avec un objet JSON valide respectant exactement ce format :
{{
  "question_json": {{"type": "html", "version": 1}} OU {{"type": "simpleText", "version": 1, "content": "..."}},
  "answers_json": {{"type": "simpleText", "version": 1, "content": [
      {{"order": 1, "type": "html"}} OU {{"order": 1, "text": "..."}}
  ]}},
  "explanation_json": {{"type": "simpleText", "version": 1, "content": [
      {{"order": 0, "text": "..."}} OU {{"order": 0, "type": "html"}}
  ]}},
  "correct_answer_order": 1,
  "slots": {{
    "question": "<!DOCTYPE html><html><head><meta charset=\\"utf-8\\"><meta name=\\"viewport\\" content=\\"width=device-width, initial-scale=1\\"><style>...</style></head><body>...</body></html>",
    "answer_2": "<!DOCTYPE html><html>...</html>"
  }}
}}

Règles STRICTES :
- Applique la règle "rendering" INDÉPENDAMMENT à CHAQUE slot : l'énoncé, CHAQUE réponse ("answer_N") et CHAQUE explication ("explanation_N") sont traités de la même façon. Un slot de réponse en "rendering": "html" produit un slot HTML au même titre que l'énoncé — ne réserve PAS le HTML au seul énoncé.
- Slot en "rendering": "html" dans le plan → l'entrée JSON correspondante est {{"type": "html"}} (avec "order" pour réponses/explications) ET le HTML du slot est présent dans "slots" (clé "question", "answer_N" ou "explanation_N").
- Slot en "rendering": "text" → texte simple dans le JSON ("content" pour la question, "text" pour réponses/explications), et RIEN dans "slots".
- Les réponses reprennent les "answer_order" du plan, dans l'ordre ; "correct_answer_order" = l'answer_order du bloc "correct": true du plan.
- "explanation_json".content : order 0 = explication générale + un order par réponse quand le plan le prévoit.
- HTML des slots : un DOCUMENT HTML COMPLET ET AUTONOME (commence par <!DOCTYPE html>, avec les balises <html>, <head> incluant <meta charset> et <meta name="viewport"> pour le responsive, et <body>). Mets tout le CSS dans un <style> du <head>. Responsive, sans JavaScript. Chaque slot est une page HTML indépendante, servie et rendue seule.
- Médias : génère <img>/<video controls>/<audio controls>/<iframe> selon le type ; retire le préfixe "//media:" dans les attributs src ; n'affiche JAMAIS l'URL brute comme texte.
- Ne génère que du JSON, aucun texte autour."""


async def generate_quiz_question_html_from_plan(
    entity_plan_json: Dict[str, Any],
    llm: Any,
    pedagogical_json: Optional[Dict[str, Any]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Génère la question de quiz riche (JSON + HTML par slot) depuis son plan d'entité."""
    prompt = ChatPromptTemplate.from_messages([("human", _QUESTION_HTML_PROMPT)])
    inputs = {
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "plan_json": json.dumps(entity_plan_json, ensure_ascii=False),
        "pedagogical_json": json.dumps(pedagogical_json or {}, ensure_ascii=False),
    }
    result = await _invoke_json(prompt, llm, inputs)

    # Nettoyage : retirer le préfixe //media: résiduel dans les slots HTML
    slots = result.get("slots", {}) or {}
    result["slots"] = {
        slot: html.replace("//media:", "") for slot, html in slots.items()
    }

    return result, prompt.format(**inputs)
