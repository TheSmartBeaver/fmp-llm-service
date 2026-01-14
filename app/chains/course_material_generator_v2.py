import json
import asyncio
from typing import Dict, Any, Union, Optional, List
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.chains.template_structure_generator import TemplateStructureGenerator
from app.utils.test import shit_test2, shit_test_3
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.chains.llm.universal_llm import create_universal_llm
from app.chains.correctors import CorrectorRegistry, processSeriesOfCorrections
from app.chains.correctors.implementations import (
    LayoutSpacingCorrector,
    DuplicateBlockRemoverCorrector,
    ListeExemplesHoistCorrector,
)
from app.chains.utils.pedagogical_json_generator import generate_pedagogical_json


class CourseMaterialGeneratorV2:
    """
    Générateur de supports de cours V2 utilisant TemplateStructureGenerator.

    Le workflow :
    1. Génère un JSON pédagogique enrichi à partir de UserEntryDto avec un LLM
    2. Utilise TemplateStructureGenerator pour mapper ce JSON vers des templates
    3. Construit le JSON final en hydratant la structure
    4. Valide et retourne le support de cours

    Avantages vs V1:
    - Cohérence globale (structure d'un seul coup vs morceaux isolés)
    - Contenu enrichi et contextualisé (pas de phrases courtes)
    - Meilleure imbrication sémantique des templates
    - Moins de duplication de contenu
    """

    def __init__(
        self,
        db_session: Session,
        embedding_model: SentenceTransformer,
        llm_config: Optional[LLMConfigDto] = None,
    ):
        """
        Args:
            db_session: Session SQLAlchemy pour accéder à la DB
            embedding_model: Modèle sentence-transformers pour les embeddings
            llm_config: Configuration optionnelle des modèles LLM à utiliser
        """
        self.db = db_session
        self.embedding_model = embedding_model
        self.llm_config = llm_config or LLMConfigDto()

        # LLM pour la génération du JSON pédagogique
        # ✅ Utilise UniversalLLM pour supporter TOUS les modèles (LangChain + Codex + O-series)
        pedagogical_model = self.llm_config.get_pedagogical_json_model()
        self.pedagogical_llm = create_universal_llm(pedagogical_model)
        # Créer le TemplateStructureGenerator avec la config LLM
        self.template_structure_generator = TemplateStructureGenerator(
            db_session=db_session,
            embedding_model=embedding_model,
            llm_config=self.llm_config,
        )

        # Initialiser le registre de correcteurs
        self.corrector_registry = self._initialize_corrector_registry()

    def generate_course_material(
        self,
        user_entry: UserEntryDto,
        top_k: int = 20,
        category_quotas: Dict[str, int] = None,
    ) -> Dict[str, Any]:
        """
        Version synchrone qui appelle la version async.
        Utilisée par Celery et autres contextes synchrones.
        """
        return asyncio.run(self.generate_course_material_async(
            user_entry=user_entry,
            top_k=top_k,
            category_quotas=category_quotas
        ))

    async def generate_course_material_async(
        self,
        user_entry: UserEntryDto,
        top_k: int = 20,
        category_quotas: Dict[str, int] = None,
    ) -> Dict[str, Any]:
        """
        Version asynchrone - Génère des supports de cours à partir d'un UserEntryDto.

        Args:
            user_entry: Contient le contexte, le contenu textuel et les médias
            top_k: Nombre de templates similaires à récupérer (défaut: 20)
            category_quotas: Dictionnaire {catégorie: quota} pour limiter par catégorie
                           Ex: {"layouts/": 5, "conceptual/": 8}

        Returns:
            Dict contenant:
            - support: Le support de cours complet structuré
            - prompts: Dict avec les prompts de chaque étape
        """
        # Étape 1: Générer le JSON pédagogique enrichi
        pedagogical_json, pedagogical_prompt = await generate_pedagogical_json(
            user_entry=user_entry,
            pedagogical_llm=self.pedagogical_llm,
        )
        
        # pedagogical_json = shit_test2
        # pedagogical_prompt = "string"

        pedagogical_json_string = json.dumps(pedagogical_json, indent=0, ensure_ascii=False)
        # print(f" pedagogical_json = {pedagogical_json_string}")

        # Étape 2: Générer la structure de templates
        context_description = self._create_context_description(user_entry)

        if category_quotas is None:
            # Par défaut: peu de layouts, plus de contenu conceptuel
            category_quotas = {"C": 2, "I": 2, "B": 2, "L": 2, "D": 2, "R": 1}

        structure_result = (
            await self.template_structure_generator.generate_template_structure(
                source_json=pedagogical_json,
                context_description=context_description,
                category_quotas=category_quotas,
                hasRealDataRendered=user_entry.hasRealDataRendered,
            )
        )

        # structure_result = {
        #     "template_structure": shit_test_3,
        #     "prompt": "SHIT",
        #     "destination_mappings": {},
        #     "debug_info": {},
        # }

        template_structure = structure_result["template_structure"]
        structure_prompt = structure_result["prompt"]
        destination_mappings = structure_result["destination_mappings"]
        debug_info = structure_result.get("debug_info", {})

        # Appliquer les corrections sur la structure de templates
        template_structure, correction_stats = processSeriesOfCorrections(
            template_structure, self.corrector_registry
        )

        # Ajouter les statistiques de correction aux debug_info
        debug_info["correction_stats"] = correction_stats



        # Étape 3: Le JSON final est déjà construit par TemplateStructureGenerator
        # Il contient la structure avec les valeurs hydratées

        # Étape 4: Validation
        validated_support = self._validate_support(template_structure)

        validated_support_string = json.dumps(
            validated_support, indent=0, ensure_ascii=False
        )
        # print(f" validated_support = {validated_support_string}")

        return {
            "support": validated_support,
            "pedagogical_json": pedagogical_json,
            "destination_mappings": destination_mappings,
            "debug_info": debug_info,
            "prompts": {
                "step1_pedagogical_json": pedagogical_prompt,
                "step2_template_structure": structure_prompt,
            },
        }


    def _create_context_description(self, user_entry: UserEntryDto) -> str:
        """
        Crée une description de contexte pour TemplateStructureGenerator.

        Args:
            user_entry: Données d'entrée de l'utilisateur

        Returns:
            String décrivant le contexte pédagogique
        """
        return f"Cours de {user_entry.context_entry.course} - Sujet: {user_entry.context_entry.topic_path}"

    def _validate_support(self, support_json: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
        """
        Valide la structure du support de cours généré.

        Args:
            support_json: JSON du support à valider (dict ou list)

        Returns:
            Support JSON validé avec version

        Raises:
            ValueError: Si le JSON est invalide
        """
        if not isinstance(support_json, (dict, list)):
            raise ValueError("Le support doit être un objet JSON ou un tableau")

        # Vérifier qu'il y a au moins un template_name quelque part dans la structure
        if not self._contains_template_name(support_json):
            raise ValueError("Le support doit contenir au moins un template_name")

        # Ajouter la version si absente (seulement si c'est un dict)
        if isinstance(support_json, dict) and "version" not in support_json:
            support_json["version"] = "1.0.0"

        return support_json

    def _contains_template_name(self, obj: Any) -> bool:
        """
        Vérifie récursivement si un objet contient au moins un template_name.

        Args:
            obj: Objet à vérifier

        Returns:
            True si un template_name est trouvé, False sinon
        """
        if isinstance(obj, dict):
            if "template_name" in obj:
                return True
            for value in obj.values():
                if self._contains_template_name(value):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if self._contains_template_name(item):
                    return True
        return False

    def _initialize_corrector_registry(self) -> CorrectorRegistry:
        """
        Crée et configure le registre de correcteurs.

        Cette méthode enregistre tous les correcteurs disponibles
        dans le système.

        Returns:
            Registre de correcteurs configuré
        """
        registry = CorrectorRegistry()

        # Enregistrer tous les correcteurs disponibles
        registry.register(LayoutSpacingCorrector())
        registry.register(DuplicateBlockRemoverCorrector())
        registry.register(ListeExemplesHoistCorrector())
        # Ajouter ici d'autres correcteurs au fur et à mesure :
        # registry.register(TextOpacityCorrector())
        # registry.register(OtherCorrector())

        return registry
