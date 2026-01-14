"""
Utilitaire pour générer un JSON pédagogique enrichi à partir de UserEntryDto.

Ce module fournit une fonction réutilisable pour la génération du JSON pédagogique,
partagée entre les différentes versions de générateurs de supports de cours.
"""
import json
from typing import Dict, Any, List, Tuple
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


async def generate_pedagogical_json(
    user_entry: UserEntryDto,
    pedagogical_llm: Any,
) -> Tuple[Dict[str, Any], str]:
    """
    Génère un JSON pédagogique enrichi à partir de UserEntryDto.

    Ce JSON contient des explications complètes, contextualisées, sans phrases courtes.
    Il structure le contenu de manière optimale pour l'apprentissage.

    Args:
        user_entry: Données d'entrée de l'utilisateur
        pedagogical_llm: LLM à utiliser pour la génération (UniversalLLM ou autre)

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

    # Créer le prompt système
    system_prompt = """Tu es un expert pédagogue spécialisé dans la structuration de contenu éducatif.

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
7. ✅ Intègre les références aux médias disponibles de manière sémantique
8. 🚫 INTERDICTION ABSOLUE: NE crée PAS d'exercices, questions, QCM, quiz ou évaluations
9. ✅ Utilise un langage clair et pédagogique, adapté à l'apprentissage
10. ⚠️ RÈGLE STRUCTURELLE CRITIQUE: Les clés (noms de propriétés) du JSON ne doivent JAMAIS représenter des valeurs ou du contenu réel
    - ❌ INTERDIT: {{"Principe de responsabilité unique": "explication..."}}
    - ❌ INTERDIT: {{"SRP": "définition...", "OCP": "définition..."}}
    - ✅ CORRECT: {{"concepts": [{{"name": "Principe de responsabilité unique", "explanation": "..."}}]}}
    - ✅ CORRECT: {{"principles": [{{"acronym": "SRP", "definition": "..."}}]}}
    - Les clés doivent être des CATÉGORIES ou des RÔLES génériques, jamais des valeurs spécifiques
"""

    user_prompt = """Voici les notes de cours brutes à transformer en JSON pédagogique optimal:

CONTENU TEXTUEL:
{text}

Génère le JSON structuré en suivant STRICTEMENT les règles ci-dessus. Développe les explications, ajoute du contexte, ne fais pas de phrases courtes."""

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

    # Pour les modèles Codex, on ne peut pas utiliser le chain operator avec JsonOutputParser
    # car il appelle la méthode sync en interne. On appelle directement le LLM.
    from app.chains.llm.universal_llm import UniversalLLM

    if isinstance(pedagogical_llm, UniversalLLM) and pedagogical_llm.use_codex_route:
        # Appel direct pour Codex (pas de chain)
        messages = prompt.format_messages(**inputs)
        response = await pedagogical_llm.ainvoke(messages)

        # Parser manuellement le JSON de la réponse
        if hasattr(response, 'content'):
            json_text = response.content
        else:
            json_text = str(response)

        result = json.loads(json_text)
    else:
        # Pour les autres modèles, utiliser la chaîne normale
        chain = prompt | pedagogical_llm | JsonOutputParser()
        result = await chain.ainvoke(inputs)

    return result, full_prompt
