"""
Utilitaire pour générer un JSON pédagogique enrichi à partir de UserEntryDto.

Ce module fournit une fonction réutilisable pour la génération du JSON pédagogique,
partagée entre les différentes versions de générateurs de supports de cours.

Deux modes sont disponibles :
- "structured" : découpe le contenu en sections thématiques (défaut historique)
- "narrative"  : génère un récit continu segmenté (narrative / aside / media)
"""
import json
from typing import Dict, Any, List, Literal, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.models.dto.user_entry.user_entry_dto import UserEntryDto


def aggregate_content(user_entry: UserEntryDto) -> Dict[str, Any]:
    """
    Agrège le contenu textuel et les médias depuis UserEntryDto.

    Args:
        user_entry: Données d'entrée de l'utilisateur

    Returns:
        Dict contenant le contenu agrégé:
        - text: Texte agrégé (book_scan + diction triés par order)
        - images: Liste des images disponibles
        - videos: Liste des vidéos disponibles
        - context: Informations de contexte (course, topic_path)
    """
    # Agréger le texte (book_scan + diction triés par order)
    text_entries = []

    # Ajouter book_scan_entry
    for entry in user_entry.book_scan_entry:
        text_entries.append(
            {"order": entry.order, "content": entry.raw_data, "type": "book_scan"}
        )

    # Ajouter diction_entry
    for entry in user_entry.diction_entry:
        # Combiner les blocs de texte
        combined_text = "\n".join(entry.text_blocs)
        text_entries.append(
            {"order": entry.order, "content": combined_text, "type": "diction"}
        )

    # Trier par order
    text_entries.sort(key=lambda x: x["order"])

    # Créer le texte agrégé
    aggregated_text = "\n\n".join([entry["content"] for entry in text_entries])

    # Agréger les médias
    images = [
        {"order": img.order, "description": img.img_description, "url": img.img_url}
        for img in user_entry.img_entry
    ]

    videos = [
        {
            "order": video.order,
            "url": video.video_url,
            "description": video.video_description,
            "start_time": video.video_start_time,
        }
        for video in user_entry.video_entry
    ]

    return {
        "text": aggregated_text,
        "images": images,
        "videos": videos,
        "context": {
            "course": user_entry.context_entry.course,
            "topic_path": user_entry.context_entry.topic_path,
        },
    }


def format_media_for_prompt(images: List[Dict], videos: List[Dict]) -> str:
    """
    Formate les médias disponibles pour inclusion dans le prompt.

    Args:
        images: Liste des images
        videos: Liste des vidéos

    Returns:
        String formaté décrivant les médias disponibles
    """
    formatted_parts = []

    if images:
        formatted_parts.append("IMAGES DISPONIBLES:")
        for i, img in enumerate(images, 1):
            formatted_parts.append(
                f"  - Image {i}: {img['description']} (URL: {img['url']})"
            )

    if videos:
        formatted_parts.append("\nVIDÉOS DISPONIBLES:")
        for i, video in enumerate(videos, 1):
            formatted_parts.append(
                f"  - Vidéo {i}: {video['description']} (URL: {video['url']}, Début: {video['start_time']})"
            )

    if not formatted_parts:
        return "Aucun média disponible."

    return "\n".join(formatted_parts)


_STRUCTURED_SYSTEM_PROMPT = """Tu es un expert spécialisé dans la reformulation et enrichissement de contenu éducatif.

CONTEXTE PÉDAGOGIQUE:
- Cours: {course}
- Chemin du sujet: {topic_path}

MÉDIAS DISPONIBLES:
{media_description}

Ta mission : transformer des notes de cours brutes en un JSON structuré OPTIMAL pour l'apprentissage.

RÈGLES CRITIQUES:
1. ✅ Crée des explications COMPLÈTES et CONTEXTUALISÉES (plusieurs phrases développées)
2. ✅ NE fais PAS de phrases trop courtes - développe les concepts avec du contexte
3. ✅ Ajoute du contexte pour faciliter la compréhension (pourquoi, comment, dans quel cas)
4. ✅ Regroupe les informations par thèmes logiques et cohérents
5. ✅ Explicite les liens entre les concepts (similitudes, différences, relations)
6. ✅ Enrichis avec des exemples concrets et pertinents
7. 🚫 INTERDICTION ABSOLUE: NE crée PAS d'exercices, questions, QCM, quiz ou évaluations
8. ✅ Utilise un langage clair et pédagogique, adapté à l'apprentissage
9. ⚠️ RÈGLE STRUCTURELLE CRITIQUE: Les clés (noms de propriétés) du JSON ne doivent JAMAIS représenter des valeurs ou du contenu réel
    - ❌ INTERDIT: {{"Principe de responsabilité unique": "explication..."}}
    - ❌ INTERDIT: {{"SRP": "définition...", "OCP": "définition..."}}
    - ✅ CORRECT: {{"concepts": [{{"name": "Principe de responsabilité unique", "explanation": "..."}}]}}
    - ✅ CORRECT: {{"principles": [{{"acronym": "SRP", "definition": "..."}}]}}
    - Les clés doivent être des CATÉGORIES ou des RÔLES génériques, jamais des valeurs spécifiques
10. ⚠️ INTÉGRATION DES MÉDIAS - RÈGLE CRITIQUE:
    - 🚫 NE regroupe PAS tous les médias dans une section ou clé unique à la fin du JSON
    - ✅ Intègre chaque média AU SEIN de la section ou du concept auquel il se rapporte
    - ✅ Pour chaque section/concept qui a un média associé, ajoute une propriété "media" contenant une URL seulement
    - ✅ Chaque URL de média est déjà préfixée par "//media:"
    - ✅ Place le média là où il est le PLUS PERTINENT pédagogiquement, pas à la fin
"""

_STRUCTURED_USER_PROMPT = """Voici les notes de cours brutes à transformer en JSON :

CONTENU TEXTUEL:
{text}

Génère le JSON structuré en suivant STRICTEMENT les règles ci-dessus. Développe les explications, ajoute du contexte, ne fais pas de phrases courtes."""


_NARRATIVE_SYSTEM_PROMPT = """Tu es un expert en narration pédagogique ET en design visuel éducatif. Tu transformes des notes de cours en un récit vivant, riche visuellement et pédagogiquement optimal.

CONTEXTE PÉDAGOGIQUE:
- Cours: {course}
- Chemin du sujet: {topic_path}

MÉDIAS DISPONIBLES:
{media_description}

Ta mission : transformer les notes de cours en un JSON narratif — un récit qui se lit d'une traite, ponctué de "pauses pédagogiques" visuellement variées et créatives.

FORMAT DE SORTIE OBLIGATOIRE:
Le JSON doit avoir exactement cette structure racine :
{{
  "segments": [ ... ]
}}

Chaque élément du tableau "segments" est un objet JSON avec a minima un champ "type" (string) que TU INVENTES librement selon ce qui sert le mieux la compréhension à cet endroit du récit.

LIBERTÉ TOTALE SUR LES TYPES DE SEGMENTS:
Tu peux inventer n'importe quel type de segment et la structure de données qui va avec. Voici des exemples pour t'inspirer — ce ne sont PAS des contraintes, juste des idées de départ :

  Récit de base :
  - {{"type": "narrative", "content": "..."}}  → prose continue, fil directeur

  Pauses visuelles enrichies (CE SONT DES EXEMPLES, SOIS CRÉATIF, NE REPRODUIS PAS LES MÊMES) :
  - {{"type": "highlight_box", "color": "#e8f4e8", "border_color": "#2d8a4e", "label": "Point clé", "content": "..."}}
  - {{"type": "comparison", "title": "...", "left_label": "...", "right_label": "...", "rows": [{{"aspect": "...", "left": "...", "right": "..."}}]}}

  Médias :
  - {{"type": "media", "url": "//media:...", "caption": "..."}}

  Mise en valeur inline dans le contenu textuel :
  - Dans les champs "content" textuels, utilise **mot** pour le gras et ==mot== pour le surlignage jaune.

Tu peux aussi inventer des types complètement nouveaux si le contenu le justifie : "character_card", "map_legend", "formula_block", "fun_fact", "analogy"...

RÈGLES ABSOLUES (les seules contraintes):
- ✅ La clé racine du JSON est TOUJOURS "segments" (tableau ordonné)
- ✅ Chaque segment a TOUJOURS un champ "type" (string)
- ✅ L'ordre des segments suit le fil logique et chronologique du contenu
- ✅ Le récit principal doit rester intelligible même sans les pauses
- ✅ Intègre les médias disponibles AU BON ENDROIT dans le récit (pas tous à la fin)
- ✅ Les URLs de médias gardent leur préfixe "//media:" intact
- 🚫 INTERDICTION ABSOLUE : NE crée PAS d'exercices, questions, QCM, quiz ou évaluations
- 🚫 NE commence PAS chaque segment narratif par un titre ou une annonce du thème
"""

_NARRATIVE_USER_PROMPT = """Voici les notes de cours brutes à transformer en récit pédagogique :

CONTENU TEXTUEL:
{text}

Génère le JSON avec la clé racine "segments". Chaque segment a un "type" que tu choisis librement pour servir au mieux la compréhension. Sois créatif sur les formats visuels : tableaux, listes, frises, encadrés colorés, définitions, comparaisons, étapes... Utilise **gras** et ==surlignage== dans les textes pour mettre en valeur les mots importants."""


async def generate_pedagogical_json(
    user_entry: UserEntryDto,
    pedagogical_llm: Any,
    mode: Literal["structured", "narrative"] = "structured",
) -> Tuple[Dict[str, Any], str]:
    """
    Génère un JSON pédagogique enrichi à partir de UserEntryDto.

    Args:
        user_entry: Données d'entrée de l'utilisateur
        pedagogical_llm: LLM à utiliser pour la génération (UniversalLLM ou autre)
        mode: "structured" (défaut) — sections thématiques ;
              "narrative" — récit continu segmenté (narrative / aside / media)

    Returns:
        Tuple contenant:
        - Dict: JSON pédagogique enrichi
        - str: Le prompt complet envoyé au LLM
    """
    # Agréger le contenu brut
    aggregated_content = aggregate_content(user_entry)

    # Formater les médias pour le prompt
    media_description = format_media_for_prompt(
        aggregated_content["images"], aggregated_content["videos"]
    )

    # Sélectionner les prompts selon le mode
    if mode == "narrative":
        system_prompt = _NARRATIVE_SYSTEM_PROMPT
        user_prompt = _NARRATIVE_USER_PROMPT
    else:
        system_prompt = _STRUCTURED_SYSTEM_PROMPT
        user_prompt = _STRUCTURED_USER_PROMPT

    # Créer le prompt template
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", user_prompt)]
    )

    # Préparer les inputs
    inputs = {
        "course": aggregated_content["context"]["course"],
        "topic_path": aggregated_content["context"]["topic_path"],
        "media_description": media_description,
        "text": aggregated_content["text"],
    }

    # Préparer le prompt complet pour le retour
    full_prompt = prompt.format(**inputs)

    from app.chains.llm.universal_llm import UniversalLLM

    if isinstance(pedagogical_llm, UniversalLLM) and pedagogical_llm.use_codex_route:
        messages = prompt.format_messages(**inputs)
        response = await pedagogical_llm.ainvoke(messages)

        if hasattr(response, 'content'):
            json_text = response.content
        else:
            json_text = str(response)

        result = json.loads(json_text)
    else:
        chain = prompt | pedagogical_llm | JsonOutputParser()
        result = await chain.ainvoke(inputs)

    return result, full_prompt
