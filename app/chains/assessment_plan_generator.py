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
import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate

from app.chains.course_plan_generator import assign_plan_ids, _find_block, _invoke_json


ANSWER_HIDDEN_MARKER = "<!--ANSWER_HIDDEN-->"

# Plafond de concurrence des appels LLM par lot de génération (quiz / cartes).
# Chaque bloc ciblé donne lieu à un appel LLM indépendant ; on les lance en
# parallèle sans dépasser cette limite pour ne pas saturer le fournisseur.
_MAX_CONCURRENCY = 5


def _single_block_plan(plan_json: Dict[str, Any], block_id: str) -> Dict[str, Any]:
    """
    Construit une vue du plan réduite au seul bloc ciblé (sa section ne
    contenant que lui), pour un appel LLM focalisé sur une entité.
    """
    section, index = _find_block(plan_json, block_id)
    if section is None:
        return {"kind": plan_json.get("kind"), "sections": []}
    focused_section = {
        k: v for k, v in section.items() if k != "blocks"
    }
    focused_section["blocks"] = [section["blocks"][index]]
    return {"kind": plan_json.get("kind"), "sections": [focused_section]}


async def _gather_limited(coros: List[Any]) -> List[Any]:
    """Exécute des coroutines en parallèle, plafonnées à _MAX_CONCURRENCY."""
    semaphore = asyncio.Semaphore(_MAX_CONCURRENCY)

    async def _run(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*[_run(c) for c in coros])


def _normalize_plan(raw: Any) -> Dict[str, Any]:
    """
    Ramène une sortie LLM hétérogène vers un plan {"sections": [...]}.

    Le JsonOutputParser peut renvoyer None (JSON "null"/vide), une liste (le LLM
    a renvoyé directement le tableau de sections), ou un dict sans "sections".
    On tolère ces variantes plutôt que de planter sur `plan["kind"] = ...`.
    """
    if isinstance(raw, dict):
        sections = raw.get("sections")
        if not isinstance(sections, list):
            # Certains LLM imbriquent le plan sous une autre clé : on récupère
            # la première liste de sections trouvée, sinon on part de vide.
            found = next(
                (v for v in raw.values() if isinstance(v, list)), []
            )
            raw = dict(raw)
            raw["sections"] = found
        return raw
    if isinstance(raw, list):
        # Le LLM a renvoyé directement la liste des sections.
        return {"sections": raw}
    # None ou scalaire : plan vide (sera signalé comme 0 bloc en amont).
    return {"sections": []}


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


def _course_assets_plan_block(assets: Optional[List[Dict[str, Any]]]) -> str:
    """
    Formate les assets réutilisables du cours pour un PROMPT DE PLAN : images
    (par nom) et ancres (par intitulé). Sert au LLM à décider s'il réutilise un
    visuel/une section du cours pour une question.
    """
    if not assets:
        return "Aucun asset réutilisable du cours."
    images = [a for a in assets if a.get("type") == "image"]
    anchors = [a for a in assets if a.get("type") == "anchor"]
    lines = ["ASSETS RÉUTILISABLES DU COURS (n'utilise QUE ceux listés ici) :"]
    if images:
        lines.append("  IMAGES DU COURS (référence par 'course_image': \"<filename>\") :")
        for img in images:
            cap = f" — {img.get('caption')}" if img.get("caption") else ""
            lines.append(f"    - {img.get('filename')}{cap}")
    if anchors:
        lines.append("  SECTIONS DU COURS (référence par 'course_anchor': \"<anchor>\") :")
        for anc in anchors:
            head = f" — {anc.get('heading')}" if anc.get("heading") else ""
            lines.append(f"    - {anc.get('anchor')}{head}")
    return "\n".join(lines)


def _course_assets_generation_block(assets: Optional[List[Dict[str, Any]]]) -> Tuple[str, List[str]]:
    """
    Formate les assets pour un PROMPT DE GÉNÉRATION FINALE : images (URL //media:
    à réutiliser) et ancres AVEC leur fragment HTML déjà extrait. Retourne aussi
    la liste des ancres SANS fragment (ignorées car introuvables ou trop
    volumineuses), pour signalement dans le résultat.
    """
    if not assets:
        return "Aucun asset réutilisable du cours.", []
    images = [a for a in assets if a.get("type") == "image"]
    anchors = [a for a in assets if a.get("type") == "anchor"]
    dropped_anchors: List[str] = []
    lines = ["ASSETS DU COURS À RÉUTILISER (n'utilise QUE ceux listés ici) :"]
    if images:
        lines.append("  IMAGES (insère <img src=\"//media:<filename>\"> — le préfixe sera retiré au rendu) :")
        for img in images:
            cap = f" — {img.get('caption')}" if img.get("caption") else ""
            lines.append(f"    - //media:{img.get('filename')}{cap}")
    for anc in anchors:
        fragment = anc.get("html_fragment")
        if fragment:
            head = f" ({anc.get('heading')})" if anc.get("heading") else ""
            lines.append(
                f"  FRAGMENT HTML de la section {anc.get('anchor')}{head} — "
                f"transplante-le tel quel si pertinent :\n{fragment}"
            )
        else:
            dropped_anchors.append(anc.get("anchor") or "?")
    return "\n".join(lines), dropped_anchors


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


def _clean_slot_html(value: Any) -> Any:
    """
    Normalise le HTML d'un slot avant renvoi au client :
    - retire le préfixe //media: ;
    - dé-échappe une string doublement encodée (JSON dans JSON) : certains
      modèles renvoient le HTML comme une string JSON quotée, laissant des \\"
      littéraux qui cassent les attributs HTML côté rendu.

    Idempotent et défensif : ne touche que ce qui en a besoin.
    """
    if not isinstance(value, str):
        return value

    html = value

    # Cas double-encodage : la valeur EST une string JSON ('"...\\"..."').
    # On tente json.loads ; s'il rend une string, c'est la vraie valeur HTML.
    stripped = html.strip()
    if len(stripped) >= 2 and stripped[0] == '"' and stripped[-1] == '"':
        try:
            decoded = json.loads(stripped)
            if isinstance(decoded, str):
                html = decoded
        except (ValueError, json.JSONDecodeError):
            pass

    # Filet de sécurité : le HTML contient des \\" (guillemets échappés) mais
    # aucun vrai " dans les attributs → échappement non résolu, on le convertit.
    if '\\"' in html and '="' not in html:
        html = html.replace('\\"', '"').replace("\\'", "'")

    return html.replace("//media:", "")


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

{course_assets_block}

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
- Couvre les points clés du contenu, du plus fondamental au plus subtil.
- RÉUTILISATION DES ASSETS DU COURS : quand une image ou une section du cours (listées dans ASSETS RÉUTILISABLES) sert vraiment une question, ajoute au bloc "course_image": "<filename>" (image à afficher) et/ou "course_anchor": "<anchor>" (section dont le visuel HTML sera réutilisé). N'utilise QUE des filenames/anchors listés ; n'en invente JAMAIS. La plupart des questions n'en ont pas besoin : n'en ajoute que si c'est pertinent.""",
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
    course_assets: Optional[List[Dict[str, Any]]] = None,
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

    # Les assets ne concernent que le quiz (images/ancres réutilisables).
    assets_block = (
        _course_assets_plan_block(course_assets) if kind == "quiz"
        else "Aucun asset réutilisable du cours."
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
        "course_assets_block": assets_block,
        "pedagogical_json": json.dumps(pedagogical_json, ensure_ascii=False),
        "course_plan_block": course_plan_block,
    }

    plan = _normalize_plan(await _invoke_json(prompt, plan_llm, inputs))
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

{course_assets_block}

La question finale est composée de SLOTS : un énoncé, des réponses ordonnées, des explications. Chaque slot sera rendu soit en texte simple, soit en HTML riche.

⚠️ SÉPARATION DES RÔLES — l'application possède SON PROPRE lecteur de quiz : elle affiche elle-même la liste des réponses, gère la sélection, la validation et l'affichage des explications. Les slots sont des CONTENUS PASSIFS injectés dans ce lecteur :
- Le slot "question" contient UNIQUEMENT le stimulus (l'énoncé) : JAMAIS la liste des options, JAMAIS de boutons radio ou « Valider », JAMAIS la bonne réponse ni sa transcription/explication.
- Chaque slot "answer_N" contient UNE seule option (son texte et/ou son média), sans lettre A/B/C/D, sans mécanique de sélection.
- Toute interactivité (choisir, valider, révéler) est INTERDITE dans les slots : elle est fournie par l'application.

Utilise exactement cette structure JSON :
{{
  "kind": "quiz_question_html",
  "sections": [
    {{ "title": "Énoncé", "slot_group": "question",
       "blocks": [ {{ "pedagogical_format": "format", "content": "...", "rendering": "html",
                      "generation_instructions": "Consignes concrètes de rendu, si utiles" }} ] }},
    {{ "title": "Réponses", "slot_group": "answers",
       "blocks": [ {{ "pedagogical_format": "réponse", "content": "...", "answer_order": 1, "correct": true, "rendering": "text" }},
                   {{ "pedagogical_format": "réponse", "content": "...", "answer_order": 2, "correct": false, "rendering": "html",
                      "url": "//media:exemple_audio.wav" }} ] }},
    {{ "title": "Explications", "slot_group": "explanations",
       "blocks": [ {{ "pedagogical_format": "explication", "content": "...", "explanation_order": 0, "rendering": "text" }} ] }}
  ]
}}

Contraintes :
- Retourne uniquement le JSON, aucune métadonnée. N'ajoute NI "id" NI "validated".
- EXACTEMENT trois sections, avec ces "slot_group" : "question", "answers", "explanations".
- Section "question" : un ou plusieurs blocs décrivant l'énoncé (texte, tableau, extrait de code...) — le stimulus SEUL, cf. SÉPARATION DES RÔLES.
- Section "answers" : 2 à 4 blocs, "answer_order" séquentiel à partir de 1, EXACTEMENT un bloc avec "correct": true. Les mauvaises réponses doivent être plausibles.
- Section "explanations" : un bloc par réponse ("explanation_order" = answer_order correspondant) + un bloc "explanation_order": 0 (explication générale) SI ELLE APPORTE QUELQUE CHOSE.
- L'explication générale (order 0) est affichée JUSTE APRÈS l'explication de la réponse choisie : elle doit la COMPLÉTER sans la répéter — règle ou concept général, mise en perspective, moyen mnémotechnique. Ne reformule JAMAIS le contenu des explications par réponse.
- L'explication générale est FACULTATIVE : si les explications par réponse se suffisent à elles-mêmes et qu'aucun apport pédagogique transversal n'existe, OMETS purement et simplement le bloc "explanation_order": 0. Mieux vaut aucune explication générale qu'une redite ou un remplissage.
- "rendering" — CHOISIS LIBREMENT au cas par cas, slot par slot, la représentation qui sert le MIEUX le contenu :
    - "html" quand le rendu riche apporte une vraie valeur.
    - "text" quand un texte simple suffit (une phrase, un mot, une valeur courte) — c'est le cas le plus fréquent, notamment pour des réponses brèves.
  N'impose ni l'un ni l'autre par principe : évalue chaque slot indépendamment. Un slot en "text" évite une génération HTML inutile.
- 🚫 MÉDIAS — RÈGLE ABSOLUE : ne crée un bloc média (avec "url") QUE pour une URL listée EXPLICITEMENT dans la section MÉDIAS JOINTS ci-dessus. S'il n'y a AUCUN média joint, n'inclus AUCUN bloc média et n'invente JAMAIS d'URL "//media:". Les URLs "//media:" présentes dans le CONTENU DE COURS appartiennent au support de cours : leurs fichiers ne sont PAS disponibles pour cette question, ne les réutilise JAMAIS.
- S'il y a des médias joints, intègre chacun dans le slot le plus pertinent (énoncé et/ou réponses), avec son URL exacte (préfixe //media: intact). Quand les médias correspondent aux OPTIONS DE RÉPONSE (ex. un audio par option), place CHAQUE URL dans le bloc "answers" de la réponse correspondante (avec "rendering": "html") — le nom du fichier et sa description indiquent à quelle réponse il appartient. Ne regroupe JAMAIS les médias des réponses dans l'énoncé.
- Si les instructions demandent un média par réponse mais que les médias joints sont moins nombreux que les réponses, n'invente RIEN : affecte les médias disponibles à leurs réponses et signale le manque dans le "content" des blocs concernés (ex. "audio manquant, à lier manuellement").
- RÉUTILISATION DES ASSETS DU COURS : si une image ou une section du cours (listées dans ASSETS RÉUTILISABLES) sert le slot, ajoute au bloc concerné "course_image": "<filename>" et/ou "course_anchor": "<anchor>". N'utilise QUE des filenames/anchors listés, jamais inventés ; le slot correspondant sera alors "rendering": "html".
- "generation_instructions" (chaîne facultative) décrit les consignes concrètes à appliquer PLUS TARD lors de la génération du bloc : dimensions ou taille maximale, placement, densité, couleurs, typographie, responsive, fichier/template exact à utiliser, etc. Renseigne-la dès qu'une précision de rendu est utile ; ne la confonds pas avec le contenu pédagogique.
- Si "generation_instructions" porte sur une mise en forme visuelle ou un média, le bloc doit avoir "rendering": "html".
- Si "generation_instructions" demande un média ou un asset, ajoute AUSSI sa référence structurée exacte au bloc ("url", "course_image" ou "course_anchor"). Ne cite jamais un fichier qui n'est pas listé dans les médias/assets disponibles.
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
    course_assets: Optional[List[Dict[str, Any]]] = None,
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
        "course_assets_block": _course_assets_plan_block(course_assets),
        "pedagogical_json": json.dumps(pedagogical_json or {}, ensure_ascii=False),
        "source_block": source_txt,
    }

    plan = _normalize_plan(await _invoke_json(prompt, plan_llm, inputs))
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
       "blocks": [ {{ "pedagogical_format": "format", "content": "...",
                      "generation_instructions": "Consignes concrètes de rendu, si utiles" }} ] }},
    {{ "title": "Réponse (fmp-hidden)", "role": "hidden",
       "blocks": [ {{ "pedagogical_format": "format", "content": "..." }} ] }}
  ]
}}

Contraintes :
- Retourne uniquement le JSON, aucune métadonnée. N'ajoute NI "id" NI "validated".
- EXACTEMENT deux sections, avec ces "role" : "visible" puis "hidden".
- Section visible : la question, avec son contexte rappelé sans trop donner d'indices.
- Section hidden : la réponse — COURTE, UNIQUE, non ambiguë, révisable en quelques secondes.
- 🚫 MÉDIAS — RÈGLE ABSOLUE : ne crée un bloc média (avec "url") QUE pour une URL listée EXPLICITEMENT dans la section MÉDIAS JOINTS ci-dessus. S'il n'y a AUCUN média joint, n'inclus AUCUN bloc média et n'invente JAMAIS d'URL "//media:". Les URLs "//media:" présentes dans le CONTENU DE COURS appartiennent au support de cours : leurs fichiers ne sont PAS disponibles pour cette carte, ne les réutilise JAMAIS.
- S'il y a des médias joints, place chacun dans la section pertinente avec son URL exacte (préfixe //media: intact).
- Pour utiliser un template fourni, crée un bloc {{"pedagogical_format": "template", "template_path": "<path>", "content": "consigne d'adaptation des champs"}}. Ne recopie JAMAIS de HTML de template : seule la référence par path compte, le HTML complet sera fourni à la génération finale.
- "generation_instructions" (chaîne facultative) décrit les consignes concrètes à appliquer PLUS TARD lors de la génération du bloc : dimensions ou taille maximale, placement, densité, couleurs, typographie, responsive, fichier/template exact à utiliser, etc. Renseigne-la dès qu'une précision de rendu est utile ; ne la confonds pas avec le contenu pédagogique.
- Si "generation_instructions" demande un média ou un template, ajoute AUSSI sa référence structurée exacte au bloc ("url" ou "template_path"). Ne cite jamais un fichier qui n'est pas listé dans les médias/templates disponibles.
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

    plan = _normalize_plan(await _invoke_json(prompt, plan_llm, inputs))
    plan["kind"] = "flashcard_full_html"
    if template_refs:
        plan["template_refs"] = template_refs
    plan = assign_plan_ids(plan)
    return plan, prompt.format(**inputs)


# ---------------------------------------------------------------------------
# Génération directe de questions depuis le plan général (mode texte classique)
# ---------------------------------------------------------------------------

_QUIZ_FROM_PLAN_PROMPT = """Tu es un expert en pédagogie et en création de contenu HTML pédagogique. Génère UNE question de quiz à partir du bloc de plan et du contenu pédagogique.

{context_block}

BLOC DU PLAN À DÉVELOPPER :
{plan_json}

CONTENU PÉDAGOGIQUE (source du détail) :
{pedagogical_json}

{course_assets_block}

Génère une question fidèle à l'esquisse du bloc (format, angle, réponse attendue). 2 à 4 réponses ; les mauvaises réponses doivent être plausibles.

CHOIX DU RENDU (html vs texte) — décide INDÉPENDAMMENT pour l'énoncé, CHAQUE réponse et CHAQUE explication :
- "text" (simple) suffit dans la grande majorité des cas : une phrase, un mot, une valeur courte.
- "html" (riche) SEULEMENT quand le rendu visuel apporte une vraie valeur : tableau, extrait de code, formule/notation, comparaison visuelle, mise en forme structurée, ou média/asset du cours à afficher.
{html_hint_block}

Réponds UNIQUEMENT avec un objet JSON valide respectant exactement ce format :
{{
  "planBlock": "{block_id}",
  "questionJson": {{"type": "html", "version": 1}} OU {{"type": "simpleText", "version": 1, "content": "TEXTE"}},
  "answersJson": {{"type": "simpleText", "version": 1, "content": [
      {{"order": 1, "type": "html"}} OU {{"order": 1, "text": "RÉPONSE"}}
  ]}},
  "explanationJson": {{"type": "simpleText", "version": 1, "content": [
      {{"order": 0, "text": "EXPLICATION_GÉNÉRALE"}} OU {{"order": 0, "type": "html"}}
  ]}},
  "correctAnswerOrder": 1,
  "slots": {{
    "question": "<!DOCTYPE html><html><head><meta charset=\\"utf-8\\"><meta name=\\"viewport\\" content=\\"width=device-width, initial-scale=1\\"><style>...</style></head><body>...</body></html>",
    "answer_2": "<!DOCTYPE html><html>...</html>"
  }}
}}

Règles STRICTES :
- Un slot en "html" → l'entrée JSON correspondante est {{"type": "html"}} (avec "order" pour réponses/explications) ET son HTML figure dans "slots" (clés "question", "answer_N", "explanation_N"). Un slot en texte → contenu textuel dans le JSON et RIEN dans "slots".
- HTML d'un slot : DOCUMENT HTML COMPLET ET AUTONOME (<!DOCTYPE html>, <html>, <head> avec <meta charset> et <meta name="viewport">, <body>), CSS dans un <style> du <head>, responsive, sans JavaScript.
- "correctAnswerOrder" = l'order de la bonne réponse ; "explanationJson".content a un order par réponse, + l'order 0 (explication générale) SEULEMENT s'il apporte quelque chose. L'explication générale est affichée JUSTE APRÈS celle de la réponse choisie : elle COMPLÈTE sans répéter (règle/concept général, mise en perspective, mnémotechnique) — jamais une reformulation des explications par réponse. Si les explications par réponse se suffisent, OMETS l'entrée order 0 : mieux vaut rien qu'une redite.
- ASSETS DU COURS : si le bloc du plan porte "course_image", insère <img src="//media:<filename>"> dans le slot HTML concerné. Si un FRAGMENT HTML d'ancre est fourni, transplante-le. N'utilise QUE les assets listés ; ne réutilise pas une ancre sans fragment fourni.
- "planBlock" reprend l'ID exact du bloc. Ne génère que du JSON, aucun texte autour."""


def _html_hint_block(hint: Optional[str]) -> str:
    """Traduit l'indice html d'un bloc en consigne pour le prompt."""
    if hint == "force_html":
        return "INDICE DE L'AUTEUR : privilégie le HTML riche pour cette question (l'énoncé au minimum)."
    if hint == "keep_simple":
        return "INDICE DE L'AUTEUR : garde cette question en texte simple, n'utilise pas de HTML."
    return "Aucun indice imposé : arbitre librement au cas par cas."


async def _generate_one_quiz_item(
    plan_json: Dict[str, Any],
    block_id: str,
    pedagogical_json: Dict[str, Any],
    llm: Any,
    context_block: str,
    assets_block: str,
) -> Optional[Dict[str, Any]]:
    """Génère UNE question de quiz (html/texte par slot) pour un seul bloc."""
    single = _single_block_plan(plan_json, block_id)
    # Indice html éventuel porté par le bloc du plan
    hint = None
    for s in single.get("sections", []):
        for b in s.get("blocks", []):
            hint = b.get("html_hint")
    prompt = ChatPromptTemplate.from_messages([("human", _QUIZ_FROM_PLAN_PROMPT)])
    inputs = {
        "context_block": context_block,
        "plan_json": json.dumps(single, ensure_ascii=False),
        "block_id": block_id,
        "pedagogical_json": json.dumps(pedagogical_json, ensure_ascii=False),
        "course_assets_block": assets_block,
        "html_hint_block": _html_hint_block(hint),
    }
    result = await _invoke_json(prompt, llm, inputs)
    if not isinstance(result, dict) or not result.get("questionJson"):
        return None

    # Nettoyage des slots (//media:, double-échappement) + traçabilité
    slots = result.get("slots") or {}
    result["slots"] = {
        slot: _clean_slot_html(html) for slot, html in slots.items()
    }
    result["planBlock"] = block_id

    # DEBUG : rendu décidé par le LLM pour cette question
    q_type = (result.get("questionJson") or {}).get("type", "?")
    ans_types = [a.get("type", "text") for a in (result.get("answersJson") or {}).get("content", [])]
    print(f"🔎 quiz-from-plan {block_id}: question={q_type}, answers={ans_types}, slots={list(result['slots'].keys())}")
    return result


async def generate_quiz_from_plan(
    plan_json: Dict[str, Any],
    target_block_ids: List[str],
    pedagogical_json: Dict[str, Any],
    llm: Any,
    course_assets: Optional[List[Dict[str, Any]]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], str, List[str]]:
    """
    Génère les questions des blocs ciblés du plan général. Chaque question peut
    être en texte simple OU en HTML (décidé par le LLM, slot par slot ; un indice
    "html_hint" du bloc peut l'influencer). Les assets du cours (images, ancres
    avec fragment) sont réutilisables.

    Un appel LLM INDÉPENDANT par bloc, en parallèle (plafond _MAX_CONCURRENCY).

    Returns:
        (items, debug_prompt, dropped_anchors) — items portent slots + planBlock.
    """
    context_block = _context_block(course_name, topic_path, additional_instructions)
    assets_block, dropped_anchors = _course_assets_generation_block(course_assets)

    results = await _gather_limited([
        _generate_one_quiz_item(
            plan_json, block_id, pedagogical_json, llm, context_block, assets_block
        )
        for block_id in target_block_ids
    ])
    items = [item for item in results if item is not None]
    debug_prompt = (
        f"{len(target_block_ids)} question(s) générée(s) en parallèle "
        f"(html/texte par slot, concurrence max {_MAX_CONCURRENCY})"
    )
    return items, debug_prompt, dropped_anchors


# ---------------------------------------------------------------------------
# Génération finale : flashcard(s) full HTML
# ---------------------------------------------------------------------------

_CARD_HTML_BASE_RULES = """RÈGLES DE LA CARTE (STRICTES) :
- Carte mentale responsive, SANS javascript, avec CSS inline, police moyenne.
- Pour CHAQUE bloc, applique fidèlement sa chaîne "generation_instructions" à sa mise en page et à son rendu. Ces consignes sont opérationnelles (dimensions, placement, style, fichier/template exact) ; ne les affiche jamais comme du texte dans la carte. Elles ne permettent toutefois pas d'inventer un média absent du plan.
- La carte prend l'espace en hauteur et n'utilise PAS de branches.
- La réponse est COURTE pour une révision rapide, UNIQUE, et on ne peut pas répondre autre chose.
- Rappelle le contexte dans la question sans trop donner d'indices.
- Ajoute une classe "fmp-hidden" sur TOUS les éléments à cacher, pour qu'on ne voie que la question, pas la réponse.
- Place le commentaire {marker} à la TOUTE FIN du HTML. C'est APRÈS ce commentaire que tu définis le code (ex: <style>) qui masque "fmp-hidden".
- Médias : n'inclus un média QUE si son URL "//media:" figure dans le PLAN fourni. N'invente JAMAIS d'URL de média et ne réutilise JAMAIS une URL "//media:" venant du CONTENU PÉDAGOGIQUE (ses fichiers ne sont pas disponibles ici). Retire le préfixe "//media:" dans les attributs src.
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


async def _generate_one_card_html(
    prompt_template: str,
    inputs: Dict[str, Any],
    llm: Any,
    plan_block: str,
) -> Dict[str, Any]:
    """
    Génère UNE carte full HTML (un appel LLM) et valide la convention du
    marqueur, avec 1 retry ciblé sur cette carte en cas d'invalidité.
    """
    prompt = ChatPromptTemplate.from_messages([("human", prompt_template)])
    result = await _invoke_json(prompt, llm, inputs)
    cards = result.get("cards", []) if isinstance(result, dict) else []
    card = cards[0] if cards else {"plan_block": plan_block, "full_html": ""}

    error = validate_full_html_marker(card.get("full_html", ""))
    if error:
        retry_template = prompt_template + (
            "\n\nATTENTION — ta précédente réponse était invalide :\n"
            f"[{plan_block}] {error}\n"
            "Corrige ce problème et régénère la carte."
        )
        retry_prompt = ChatPromptTemplate.from_messages([("human", retry_template)])
        result = await _invoke_json(retry_prompt, llm, inputs)
        cards = result.get("cards", []) if isinstance(result, dict) else []
        card = cards[0] if cards else {"plan_block": plan_block, "full_html": ""}
        remaining = validate_full_html_marker(card.get("full_html", ""))
        if remaining:
            raise ValueError(
                f"Carte full HTML invalide après retry [{plan_block}] : {remaining}"
            )

    card["plan_block"] = plan_block  # traçabilité garantie
    return card


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
    """
    Génère les cartes full HTML des blocs ciblés du plan général.

    Un appel LLM INDÉPENDANT par carte, lancés en parallèle (plafond
    _MAX_CONCURRENCY), avec retry ciblé par carte invalide.
    """
    context_block = _context_block(course_name, topic_path, additional_instructions)
    templates_block = _templates_full_block(templates)

    def _inputs_for(block_id: str) -> Dict[str, Any]:
        return {
            "context_block": context_block,
            "plan_json": json.dumps(_single_block_plan(plan_json, block_id), ensure_ascii=False),
            "target_block_ids": block_id,
            "pedagogical_json": json.dumps(pedagogical_json, ensure_ascii=False),
            "templates_block": templates_block,
            "marker": ANSWER_HIDDEN_MARKER,
        }

    cards = await _gather_limited([
        _generate_one_card_html(_CARDS_FROM_PLAN_PROMPT, _inputs_for(block_id), llm, block_id)
        for block_id in target_block_ids
    ])
    debug_prompt = (
        f"{len(target_block_ids)} carte(s) générée(s) en parallèle "
        f"(1 appel LLM/carte, concurrence max {_MAX_CONCURRENCY})"
    )
    return cards, debug_prompt


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
    card = await _generate_one_card_html(
        _CARD_HTML_FROM_ENTITY_PLAN_PROMPT, inputs, llm, plan_block="root"
    )
    debug_prompt = ChatPromptTemplate.from_messages(
        [("human", _CARD_HTML_FROM_ENTITY_PLAN_PROMPT)]
    ).format(**inputs)
    return [card], debug_prompt


# ---------------------------------------------------------------------------
# Génération finale : question de quiz HTML (par slots)
# ---------------------------------------------------------------------------

_QUESTION_HTML_PROMPT = """Tu es un expert en création de contenu HTML pédagogique. Tu génères UNE question de quiz riche à partir de son plan de construction validé.

{context_block}

PLAN DE CONSTRUCTION VALIDÉ (suis-le STRICTEMENT — sections "question" / "answers" / "explanations") :
{plan_json}

CONTENU PÉDAGOGIQUE (source du détail) :
{pedagogical_json}

{course_assets_block}

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
- ⚠️ SLOTS PASSIFS — l'application possède SON PROPRE lecteur de quiz (affichage des options, sélection, validation, explications). Les slots sont des contenus statiques injectés dans ce lecteur : AUCUN <input>, <button>, <form>, AUCUNE mécanique de sélection/validation/révélation. Le slot "question" contient UNIQUEMENT le stimulus : JAMAIS la liste des options de réponse, JAMAIS la bonne réponse ni sa transcription/explication. Chaque slot "answer_N" contient UNE seule option (sans lettre A/B/C/D). Si les "generation_instructions" d'un bloc décrivent des options, boutons ou révélation de réponse, IGNORE cette partie : ne garde que ce qui concerne le contenu propre du slot.
- Pour CHAQUE bloc, applique fidèlement sa chaîne "generation_instructions" au slot correspondant. Ces consignes sont opérationnelles (dimensions, placement, style, fichier/template exact) ; ne les affiche jamais comme du texte dans le slot. Elles ne permettent toutefois pas d'inventer un média ou un asset absent du plan et de la liste fournie.
- Applique la règle "rendering" INDÉPENDAMMENT à CHAQUE slot : l'énoncé, CHAQUE réponse ("answer_N") et CHAQUE explication ("explanation_N") sont traités de la même façon. Un slot de réponse en "rendering": "html" produit un slot HTML au même titre que l'énoncé — ne réserve PAS le HTML au seul énoncé.
- Slot en "rendering": "html" dans le plan → l'entrée JSON correspondante est {{"type": "html"}} (avec "order" pour réponses/explications) ET le HTML du slot est présent dans "slots" (clé "question", "answer_N" ou "explanation_N").
- Slot en "rendering": "text" → texte simple dans le JSON ("content" pour la question, "text" pour réponses/explications), et RIEN dans "slots".
- Les réponses reprennent les "answer_order" du plan, dans l'ordre ; "correct_answer_order" = l'answer_order du bloc "correct": true du plan.
- "explanation_json".content : un order par réponse quand le plan le prévoit, + l'order 0 (explication générale) UNIQUEMENT si le plan en contient un. L'explication générale est affichée JUSTE APRÈS celle de la réponse choisie : elle COMPLÈTE sans répéter (règle/concept général, mise en perspective, mnémotechnique) — jamais une reformulation des explications par réponse. Si le plan n'a pas de bloc "explanation_order": 0, n'en invente PAS : omets simplement l'entrée order 0.
- HTML des slots : un DOCUMENT HTML COMPLET ET AUTONOME (commence par <!DOCTYPE html>, avec les balises <html>, <head> incluant <meta charset> et <meta name="viewport"> pour le responsive, et <body>). Mets tout le CSS dans un <style> du <head>. Responsive, sans JavaScript. Chaque slot est une page HTML indépendante, servie et rendue seule.
- Médias : n'inclus un média QUE si son URL "//media:" figure dans le PLAN DE CONSTRUCTION VALIDÉ ci-dessus. N'invente JAMAIS d'URL de média et ne réutilise JAMAIS une URL "//media:" venant du CONTENU PÉDAGOGIQUE (ses fichiers ne sont pas disponibles ici). Pour un média du plan : génère <img>/<video controls>/<audio controls>/<iframe> selon le type ; retire le préfixe "//media:" dans les attributs src ; n'affiche JAMAIS l'URL brute comme texte.
- ASSETS DU COURS (section "ASSETS DU COURS À RÉUTILISER" ci-dessus) : si le bloc du plan porte "course_image", insère l'image correspondante via <img src="//media:<filename>">. Si le bloc porte "course_anchor" et qu'un FRAGMENT HTML est fourni pour cette ancre, transplante ce fragment dans le slot HTML. N'utilise QUE les assets listés ; ne réutilise pas une ancre sans fragment fourni.
- Ne génère que du JSON, aucun texte autour."""


async def generate_quiz_question_html_from_plan(
    entity_plan_json: Dict[str, Any],
    llm: Any,
    pedagogical_json: Optional[Dict[str, Any]] = None,
    course_assets: Optional[List[Dict[str, Any]]] = None,
    course_name: Optional[str] = None,
    topic_path: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> Tuple[Dict[str, Any], str, List[str]]:
    """
    Génère la question de quiz riche (JSON + HTML par slot) depuis son plan
    d'entité, en réutilisant les assets du cours fournis.

    Returns:
        (result, prompt, dropped_anchors) — dropped_anchors liste les ancres
        référencées mais ignorées (fragment introuvable ou trop volumineux).
    """
    assets_block, dropped_anchors = _course_assets_generation_block(course_assets)

    prompt = ChatPromptTemplate.from_messages([("human", _QUESTION_HTML_PROMPT)])
    inputs = {
        "context_block": _context_block(course_name, topic_path, additional_instructions),
        "plan_json": json.dumps(entity_plan_json, ensure_ascii=False),
        "pedagogical_json": json.dumps(pedagogical_json or {}, ensure_ascii=False),
        "course_assets_block": assets_block,
    }
    result = await _invoke_json(prompt, llm, inputs)

    # Nettoyage des slots (//media:, double-échappement)
    slots = result.get("slots", {}) or {}
    result["slots"] = {
        slot: _clean_slot_html(html) for slot, html in slots.items()
    }

    return result, prompt.format(**inputs), dropped_anchors
