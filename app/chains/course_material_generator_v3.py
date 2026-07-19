"""
Générateur de supports de cours V3 - Génération HTML par groupe.

Ce générateur utilise une approche différente de V2 :
- Génère d'abord un JSON pédagogique enrichi
- Construit un mapping chemin -> valeur
- Groupe les chemins par préfixe
- Génère du HTML pour chaque groupe en parallèle via LLM
"""
import json
import re
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate

from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.chains.llm.universal_llm import create_universal_llm, UniversalLLM
from app.chains.utils.path_mapper import build_path_to_value_map
from app.chains.utils.pedagogical_json_generator import generate_pedagogical_json


class CourseMaterialGeneratorV3:
    """
    Générateur de supports de cours V3 utilisant la génération HTML par groupe.

    Le workflow :
    1. Génère un JSON pédagogique enrichi à partir de UserEntryDto
    2. Construit un mapping chemin -> valeur à partir du JSON pédagogique
    3. Groupe les chemins par leur premier préfixe
    4. Génère du HTML pour chaque groupe en parallèle via LLM
    5. Retourne les supports HTML avec le JSON pédagogique et les debug info

    Différences avec V2:
    - Pas de mapping vers templates
    - Génération HTML directe via LLM
    - Traitement parallèle par groupe
    - CSS inline dans les balises HTML
    """

    def __init__(
        self,
        db_session: Session,
        embedding_model: SentenceTransformer,
        llm_config: Optional[LLMConfigDto] = None,
    ):
        """
        Args:
            db_session: Session SQLAlchemy pour accéder à la DB (non utilisé en V3 mais gardé pour compatibilité)
            embedding_model: Modèle sentence-transformers (non utilisé en V3 mais gardé pour compatibilité)
            llm_config: Configuration optionnelle des modèles LLM à utiliser
        """
        self.db = db_session
        self.embedding_model = embedding_model
        self.llm_config = llm_config or LLMConfigDto()

        # LLM pour la génération du JSON pédagogique
        pedagogical_model = self.llm_config.get_pedagogical_json_model()
        self.pedagogical_llm = create_universal_llm(pedagogical_model)
        self.pedagogical_mode = self.llm_config.pedagogical_json_mode

        # LLM pour la génération du HTML par groupe
        path_groups_model = self.llm_config.get_path_groups_model()
        self.path_groups_llm = create_universal_llm(path_groups_model)

    def generate_course_material(
        self,
        user_entry: UserEntryDto,
        plan_json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Version synchrone qui appelle la version async.
        Utilisée par Celery et autres contextes synchrones.

        Args:
            user_entry: Contient le contexte, le contenu textuel et les médias
            plan_json: Plan de cours validé optionnel ({"sections": [...]}) ; s'il est
                fourni, le JSON pédagogique est généré sous contrainte stricte du plan

        Returns:
            Dict contenant:
            - htmlSupports: Dict {group_name: html_content}
            - pedagogical_json: Le JSON pédagogique généré
            - debug_info: Informations de debug
        """
        return asyncio.run(
            self.generate_course_material_async(user_entry=user_entry, plan_json=plan_json)
        )

    def modify_course_material(
        self,
        pedagogical_json: Dict[str, Any],
        modification_instructions: str,
        user_entry: Optional["UserEntryDto"] = None,
    ) -> Dict[str, Any]:
        """Version synchrone de modify_course_material_async. Utilisée par Celery."""
        return asyncio.run(
            self.modify_course_material_async(pedagogical_json, modification_instructions, user_entry)
        )

    async def modify_course_material_async(
        self,
        pedagogical_json: Dict[str, Any],
        modification_instructions: str,
        user_entry: Optional["UserEntryDto"] = None,
    ) -> Dict[str, Any]:
        """
        Modifie un JSON pédagogique narratif existant selon des instructions libres,
        puis régénère le HTML correspondant.

        Args:
            pedagogical_json: JSON narratif déjà généré (avec clé "segments")
            modification_instructions: Instructions libres de modification
            user_entry: Données source optionnelles (peut contenir de nouveaux médias ou textes)

        Returns:
            Dict contenant htmlSupports, pedagogical_json modifié, debug_info
        """
        from app.chains.utils.pedagogical_json_generator import aggregate_content, format_media_for_prompt

        source_block = ""
        if user_entry is not None:
            aggregated = aggregate_content(user_entry)
            media_description = format_media_for_prompt(aggregated["images"], aggregated["videos"])
            source_block = f"""
CONTENU SOURCE (peut contenir de nouvelles informations à intégrer) :
{aggregated["text"]}

MÉDIAS DISPONIBLES :
{media_description}
"""

        system_prompt = """Tu es un expert en narration pédagogique et design visuel éducatif.

Ton rôle est de MODIFIER un JSON narratif pédagogique existant selon les instructions fournies.

RÈGLES ABSOLUES:
1. Tu dois MODIFIER le JSON existant, pas en créer un nouveau de zéro
2. Conserve tous les segments non concernés par les modifications
3. La clé racine doit rester "segments" (tableau ordonné)
4. Chaque segment doit toujours avoir un champ "type"
5. Tu peux ajouter, supprimer, réordonner ou modifier des segments
6. Tu peux inventer de nouveaux types de segments si les instructions le demandent
7. Dans les champs textuels, utilise **mot** pour le gras et ==mot== pour le surlignage
8. Les URLs de médias gardent leur préfixe "//media:" intact
9. 🚫 INTERDICTION ABSOLUE : NE crée PAS d'exercices, questions, QCM, quiz ou évaluations
"""

        user_prompt = """Voici le JSON narratif pédagogique existant à modifier :

{existing_json}
{source_block}
INSTRUCTIONS DE MODIFICATION :
{instructions}

Génère le JSON modifié avec la clé racine "segments". Retourne UNIQUEMENT le JSON valide, sans explications."""

        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", user_prompt)]
        )

        inputs = {
            "existing_json": json.dumps(pedagogical_json, ensure_ascii=False, indent=2),
            "source_block": source_block,
            "instructions": modification_instructions,
        }

        from langchain_core.output_parsers import JsonOutputParser

        if isinstance(self.pedagogical_llm, UniversalLLM) and self.pedagogical_llm.use_codex_route:
            messages = prompt.format_messages(**inputs)
            response = await self.pedagogical_llm.ainvoke(messages)
            json_text = response.content if hasattr(response, "content") else str(response)
            modified_json = json.loads(json_text)
        else:
            chain = prompt | self.pedagogical_llm | JsonOutputParser()
            modified_json = await chain.ainvoke(inputs)

        modification_prompt = prompt.format(**inputs)

        result = await self._generate_from_narrative_json(modified_json, modification_prompt)
        result["debug_info"]["modification_instructions"] = modification_instructions
        return result

    async def generate_course_material_async(
        self,
        user_entry: UserEntryDto,
        plan_json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Version asynchrone - Génère des supports de cours HTML à partir d'un UserEntryDto.

        Workflow en 5 étapes:
        1. Génération du JSON pédagogique enrichi
        2. Construction du mapping chemin -> valeur
        3. Groupement des chemins par préfixe
        4. Génération HTML parallèle pour chaque groupe
        5. Retour du résultat structuré

        Args:
            user_entry: Contient le contexte, le contenu textuel et les médias
            plan_json: Plan de cours validé optionnel ; s'il est fourni, le JSON
                pédagogique est généré au format narratif sous contrainte du plan
                (mêmes sections, mêmes blocs, mêmes formats, médias en place)

        Returns:
            Dict contenant:
            - htmlSupports: Dict {group_name: html_content}
            - pedagogical_json: Le JSON pédagogique généré
            - debug_info: Informations de debug
        """
        # Mode plan : le pedagogical_json est contraint par le plan validé et
        # sort au format narratif ("segments"), rendu par le pipeline narratif.
        if plan_json is not None:
            from app.chains.utils.pedagogical_json_generator import (
                generate_pedagogical_json_from_plan,
            )

            pedagogical_json, pedagogical_prompt = await generate_pedagogical_json_from_plan(
                user_entry=user_entry,
                plan_json=plan_json,
                pedagogical_llm=self.pedagogical_llm,
            )
            result = await self._generate_from_narrative_json(
                pedagogical_json, pedagogical_prompt
            )
            result["debug_info"]["mode"] = "plan_constrained"
            result["debug_info"]["plan_json"] = plan_json
            return result

        # Étape 1: Générer le JSON pédagogique enrichi
        pedagogical_json, pedagogical_prompt = await generate_pedagogical_json(
            user_entry=user_entry,
            pedagogical_llm=self.pedagogical_llm,
            mode=self.pedagogical_mode,
        )

        if self.pedagogical_mode == "narrative":
            return await self._generate_from_narrative_json(
                pedagogical_json, pedagogical_prompt
            )

        # Étape 2: Construire le mapping chemin -> valeur
        path_to_value_map = build_path_to_value_map(pedagogical_json)

        # Étape 3: Grouper les chemins par premier préfixe
        path_groups = self._group_paths_by_first_prefix(path_to_value_map)

        # Étape 4: Générer HTML en parallèle pour chaque groupe
        tasks = [
            self._generate_html_for_group(group_name, group_paths)
            for group_name, group_paths in path_groups.items()
        ]
        html_results = await asyncio.gather(*tasks)

        # Construire le dictionnaire des supports HTML
        html_supports = {
            group_name: html_content
            for group_name, html_content in zip(path_groups.keys(), html_results)
        }

        # Étape 5: Retourner le résultat structuré
        return {
            "htmlSupports": html_supports,
            "pedagogical_json": pedagogical_json,
            "debug_info": {
                "pedagogical_prompt": pedagogical_prompt,
                "path_to_value_map": path_to_value_map,
                "path_groups": list(path_groups.keys()),
                "num_groups": len(path_groups),
                "num_paths": len(path_to_value_map),
            },
        }

    async def _generate_from_narrative_json(
        self,
        pedagogical_json: Dict[str, Any],
        pedagogical_prompt: str,
    ) -> Dict[str, Any]:
        """
        Construit le résultat HTML à partir d'un JSON narratif segmenté.

        Chaque segment est rendu via un appel LLM indépendant (en parallèle),
        ce qui permet de gérer n'importe quelle structure de segment inventée
        par le LLM de génération.
        """
        segments = pedagogical_json.get("segments", [])

        tasks = [self._render_narrative_segment_llm(seg, i) for i, seg in enumerate(segments)]
        html_parts = await asyncio.gather(*tasks)
        narrative_html = "\n".join(html_parts)

        return {
            "htmlSupports": {"narrative": narrative_html},
            "pedagogical_json": pedagogical_json,
            "debug_info": {
                "pedagogical_prompt": pedagogical_prompt,
                "mode": "narrative",
                "num_segments": len(segments),
            },
        }

    async def _render_narrative_segment_llm(
        self, segment: Dict[str, Any], index: int, retry_count: int = 0
    ) -> str:
        """
        Génère le HTML d'un segment narratif via LLM.

        Accepte n'importe quelle structure de segment JSON — le LLM de rendu
        adapte le visuel à la structure qu'il reçoit.
        """
        seg_type = segment.get("type", "unknown")

        # Les segments "narrative" purs sont rendus directement sans appel LLM
        # pour éviter de surcharger inutilement et préserver la fluidité du texte.
        if seg_type == "narrative":
            content = segment.get("content", "")
            content = self._render_inline_markers(content)
            return (
                f'<p style="max-width: 38rem; margin: 0 auto; padding: 2rem 1.5rem; '
                f'font-family: \'Iowan Old Style\', \'Palatino Linotype\', Palatino, Georgia, serif; '
                f'font-size: 1.1875rem; line-height: 1.75; color: #2b2926; background: #faf8f5; '
                f'text-align: justify; text-wrap: pretty; hyphens: auto; '
                f'-webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; '
                f'white-space: pre-wrap;">'
                f'{content}</p>'
            )

        # Les segments "media" sont rendus directement (logique déterministe sur l'URL)
        if seg_type == "media":
            return self._render_media_segment(segment)

        # Les titres de section (mode plan) sont rendus directement
        if seg_type == "section_title":
            title = self._render_inline_markers(segment.get("content", ""))
            return (
                f'<h2 style="max-width: 38rem; margin: 0 auto; padding: 2.5rem 1.5rem 0.5rem; '
                f'font-family: system-ui, sans-serif; font-size: 1.5rem; font-weight: 700; '
                f'color: #1a2733; border-bottom: 2px solid #4a7fcb; '
                f'-webkit-font-smoothing: antialiased;">'
                f'{title}</h2>'
            )

        try:
            system_prompt = """Tu es un expert en design HTML pédagogique et visuel.

Ta mission : générer le rendu HTML d'UN segment pédagogique à partir de sa structure JSON.

RÈGLES CRITIQUES:
1. ✅ Génère UNIQUEMENT le fragment HTML du segment (pas de <!DOCTYPE>, <html>, <head>, <body>)
2. ✅ Écris le CSS directement dans les balises HTML (style="...") — PAS de classes CSS
3. ✅ Adapte créativement le rendu visuel au type et au contenu du segment
4. ✅ Utilise des éléments HTML sémantiques appropriés (table, ul, ol, aside, figure, blockquote, etc.)
5. ✅ Le rendu doit être visuellement riche, lisible et pédagogiquement efficace
6. ✅ Assure-toi que le HTML est valide et bien formaté
7. 🚫 NE génère PAS de JavaScript
8. 🚫 NE génère PAS de liens externes non fournis dans les données
9. ⚠️ GESTION DES MÉDIAS:
   - Les URLs de médias ont le préfixe "//media:" — retire-le dans les attributs src
   - ✅ Génère <img> pour les images, <video controls> pour les vidéos, <iframe> pour YouTube/Vimeo
   - 🚫 NE affiche JAMAIS l'URL brute comme du texte
10. ⚠️ MISE EN VALEUR INLINE:
    - **mot** dans le texte → <strong>mot</strong>
    - ==mot== dans le texte → <mark style="background:#fff176; padding:0 2px;">mot</mark>

GUIDE DE STYLE:
- Police: system-ui, sans-serif
- Espacement généreux, marges verticales entre 1em et 2em
- Encadrés: border-radius 6-8px, padding 12-20px
- Tableaux: border-collapse collapse, alternance de fond sur les lignes
- Frises chronologiques: disposition horizontale ou verticale avec connecteurs visuels
- Citations: border-left colorée, italique, couleur atténuée
- Couleurs d'accent: choisis parmi bleu (#4a7fcb), vert (#2d8a4e), orange (#e07b39), violet (#7c5cbf), rouge (#c0392b) selon le ton du segment
"""

            user_prompt = """Génère le rendu HTML de ce segment pédagogique :

TYPE: {seg_type}

DONNÉES JSON:
{segment_json}

Retourne UNIQUEMENT le fragment HTML, sans explications ni balises de code markdown."""

            prompt = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("human", user_prompt)]
            )

            inputs = {
                "seg_type": seg_type,
                "segment_json": json.dumps(segment, ensure_ascii=False, indent=2),
            }

            if isinstance(self.path_groups_llm, UniversalLLM) and self.path_groups_llm.use_codex_route:
                messages = prompt.format_messages(**inputs)
                response = await self.path_groups_llm.ainvoke(messages)
                html_content = response.content.strip() if hasattr(response, "content") else str(response).strip()
            else:
                chain = prompt | self.path_groups_llm
                response = await chain.ainvoke(inputs)
                html_content = response.content.strip() if hasattr(response, "content") else str(response).strip()

            return self._strip_media_prefix(html_content)

        except Exception as e:
            if retry_count < 1:
                return await self._render_narrative_segment_llm(segment, index, retry_count + 1)
            # Fallback lisible en cas d'échec persistant
            return (
                f'<div style="border:1px solid #ddd; padding:12px; margin:1em 0; '
                f'border-radius:6px; font-family:system-ui,sans-serif; color:#555;">'
                f'{json.dumps(segment, ensure_ascii=False)}</div>'
            )

    @staticmethod
    def _render_inline_markers(text: str) -> str:
        """Convertit **gras** et ==surligné== en balises HTML inline."""
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'==(.+?)==', r'<mark style="background:#fff176;padding:0 2px;">\1</mark>', text)
        return text

    @staticmethod
    def _render_media_segment(segment: Dict[str, Any]) -> str:
        """Rendu déterministe d'un segment media (image, vidéo, iframe)."""
        url = segment.get("url", "")
        caption = segment.get("caption", "")
        clean_url = url.replace("//media:", "")
        is_video = any(ext in clean_url.lower() for ext in [".mp4", ".webm", ".ogg"])
        is_youtube = "youtube.com" in clean_url or "youtu.be" in clean_url
        is_vimeo = "vimeo.com" in clean_url

        if is_youtube or is_vimeo:
            media_tag = (
                f'<iframe src="{clean_url}" style="width:100%; aspect-ratio:16/9; '
                f'border:none; border-radius:6px;" allowfullscreen></iframe>'
            )
        elif is_video:
            media_tag = (
                f'<video controls style="width:100%; border-radius:6px;">'
                f'<source src="{clean_url}"></video>'
            )
        else:
            media_tag = (
                f'<img src="{clean_url}" alt="{caption}" '
                f'style="max-width:100%; border-radius:6px; display:block; margin:0 auto;">'
            )

        return (
            f'<figure style="margin: 1.5em 0; text-align: center;">'
            f'{media_tag}'
            f'<figcaption style="font-family: system-ui, sans-serif; font-size: 0.85rem; '
            f'color: #555; margin-top: 8px; font-style: italic;">{caption}</figcaption>'
            f'</figure>'
        )

    def _group_paths_by_first_prefix(
        self, path_to_value_map: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Regroupe les chemins par leur premier préfixe (avant le premier '->' ou '[').

        Le premier segment du chemin détermine le groupe d'appartenance.

        Args:
            path_to_value_map: Dictionnaire {chemin: valeur}

        Returns:
            Dictionnaire {group_name: {chemin: valeur}}

        Exemple:
            Input: {
                "metadata->course": "Espagnol",
                "metadata->language": "fr",
                "concepts[0]->name": "Présent",
                "concepts[0]->desc": "...",
                "examples[0]->verb": "hablar"
            }
            Output: {
                "metadata": {
                    "metadata->course": "Espagnol",
                    "metadata->language": "fr"
                },
                "concepts": {
                    "concepts[0]->name": "Présent",
                    "concepts[0]->desc": "..."
                },
                "examples": {
                    "examples[0]->verb": "hablar"
                }
            }
        """
        groups = {}

        for path, value in path_to_value_map.items():
            # Extraire le premier segment (avant '->' ou '[')
            if '->' in path:
                prefix = path.split('->')[0]
            elif '[' in path:
                prefix = path.split('[')[0]
            else:
                # Cas où le chemin n'a qu'un seul segment
                prefix = path

            # Créer le groupe si nécessaire
            if prefix not in groups:
                groups[prefix] = {}

            # Ajouter le chemin au groupe
            groups[prefix][path] = value

        return groups

    @staticmethod
    def _strip_media_prefix(html: str) -> str:
        """
        Retire le préfixe "//media:" des URLs dans le HTML généré par le LLM.

        Le LLM peut laisser le préfixe dans les attributs src, href ou comme texte brut.
        Ce parseur couvre les trois cas avec une regex sur l'ensemble du HTML.

        Args:
            html: HTML brut potentiellement contenant des occurrences de "//media:"

        Returns:
            HTML avec toutes les occurrences de "//media:" supprimées
        """
        return re.sub(r'//media:', '', html)

    async def _generate_html_for_group(
        self, group_name: str, group_paths: Dict[str, Any], retry_count: int = 0
    ) -> str:
        """
        Génère une div HTML représentant les données d'un groupe.

        Utilise self.path_groups_llm pour générer du HTML pédagogique.
        Le CSS est écrit directement dans les balises (inline styles).

        En cas d'erreur, réessaie une fois. Si l'échec persiste, retourne un HTML avec le message d'erreur.

        Args:
            group_name: Nom du groupe
            group_paths: Dictionnaire {chemin: valeur} pour ce groupe
            retry_count: Nombre de tentatives déjà effectuées (pour la logique de retry)

        Returns:
            String contenant le HTML de la div
        """
        try:
            # Créer le prompt pour la génération HTML
            system_prompt = """Tu es un expert en création de contenu HTML pédagogique.

Ta mission : générer une div HTML qui représente de manière optimale les données fournies.

RÈGLES CRITIQUES:
1. ✅ Génère UNIQUEMENT le contenu HTML de la div (pas de <!DOCTYPE>, <html>, <head>, <body>)
2. ✅ Écris le CSS directement dans les balises HTML (style="...") - PAS de classes CSS
3. ✅ Structure le contenu de manière claire et pédagogique
4. ✅ Utilise des éléments HTML sémantiques appropriés (h1-h6, p, ul, ol, table, etc.)
5. ✅ Assure-toi que le HTML est valide et bien formaté
6. ✅ Adapte la présentation au type de contenu (liste, tableau, paragraphes, etc.)
7. ✅ Utilise des couleurs et styles sobres et professionnels
8. 🚫 NE génère PAS de JavaScript
9. 🚫 NE génère PAS de liens externes non fournis dans les données
10. ⚠️ GESTION DES MÉDIAS - RÈGLE CRITIQUE:
    - Certaines valeurs sont des URLs de médias, identifiables par le préfixe "//media:"
    - ✅ Génère une balise <img> pour les images
    - ✅ Génère une balise <video controls> pour les vidéos
    - ✅ Génère une balise <iframe> pour les vidéos YouTube ou Vimeo
    - 🚫 NE affiche JAMAIS l'URL brute comme du texte

STYLE RECOMMANDÉ:
- Police: system-ui, sans-serif
- Couleurs: tons neutres (gris, bleu, vert pour accents)
- Espacements: généreux pour la lisibilité
- Bordures: subtiles (1px solid #ddd)
"""

            user_prompt = """Génère une div HTML pour représenter ces données pédagogiques:

GROUPE: {group_name}

DONNÉES:
{group_data}

Retourne UNIQUEMENT le HTML de la div, sans explications."""

            prompt = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("human", user_prompt)]
            )

            # Formater les données du groupe pour le prompt
            group_data_lines = []
            for path, value in group_paths.items():
                # Formatter la valeur de manière lisible
                if isinstance(value, str):
                    formatted_value = f'"{value}"'
                else:
                    formatted_value = str(value)
                group_data_lines.append(f"{path}: {formatted_value}")

            group_data_str = "\n".join(group_data_lines)

            # Préparer les inputs
            inputs = {
                "group_name": group_name,
                "group_data": group_data_str,
            }

            # Appeler le LLM
            if isinstance(self.path_groups_llm, UniversalLLM) and self.path_groups_llm.use_codex_route:
                # Appel direct pour Codex
                messages = prompt.format_messages(**inputs)
                response = await self.path_groups_llm.ainvoke(messages)

                if hasattr(response, 'content'):
                    html_content = response.content.strip()
                else:
                    html_content = str(response).strip()
            else:
                # Pour les autres modèles
                chain = prompt | self.path_groups_llm
                response = await chain.ainvoke(inputs)

                if hasattr(response, 'content'):
                    html_content = response.content.strip()
                else:
                    html_content = str(response).strip()

            return self._strip_media_prefix(html_content)

        except Exception as e:
            # En cas d'erreur, réessayer une fois
            if retry_count < 1:
                return await self._generate_html_for_group(
                    group_name, group_paths, retry_count + 1
                )
            else:
                # Après 2 tentatives, retourner un HTML avec le message d'erreur
                error_html = f"""<div style="border: 2px solid #ff4444; background-color: #fff5f5; padding: 20px; border-radius: 8px; font-family: system-ui, sans-serif;">
    <h3 style="color: #cc0000; margin-top: 0;">Erreur de génération - Groupe: {group_name}</h3>
    <p style="color: #666;">Une erreur est survenue lors de la génération du contenu HTML pour ce groupe.</p>
    <details style="margin-top: 10px;">
        <summary style="cursor: pointer; color: #0066cc;">Détails de l'erreur</summary>
        <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px;">{str(e)}</pre>
    </details>
    <details style="margin-top: 10px;">
        <summary style="cursor: pointer; color: #0066cc;">Données brutes du groupe</summary>
        <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px;">{json.dumps(group_paths, indent=2, ensure_ascii=False)}</pre>
    </details>
</div>"""
                return error_html
