"""
Wrapper LLM universel qui supporte à la fois les modèles LangChain standard
et les modèles Codex/O-series via la route /api/utils/codex.

Ce wrapper permet d'utiliser n'importe quel modèle de manière transparente,
en détectant automatiquement quel endpoint utiliser.
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional, Union, ClassVar
from pydantic import Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun

from app.chains.llm.llm_factory import LLMModelFactory, LLMModel


class UniversalLLM(BaseChatModel):
    """
    Wrapper LLM universel qui supporte:
    - Modèles LangChain standard (Anthropic, Gemini, GPT via /v1/chat/completions)
    - Modèles Codex/O-series (via route /api/utils/codex → /v1/responses)

    Usage:
        # Avec un modèle standard (LangChain)
        llm = UniversalLLM(model=LLMModel.CLAUDE_HAIKU_4_5_20251001)

        # Avec un modèle Codex (via route dédiée)
        llm = UniversalLLM(
            model_name="gpt-5.1-codex",
            use_codex_route=True,
            api_base_url="http://localhost:8000"
        )

        # Appel uniforme
        result = llm.invoke("Write a fibonacci function")
    """

    # Modèles qui nécessitent la route Codex
    CODEX_MODELS: ClassVar[set] = {
        "gpt-5.1-codex-max",
        "gpt-5.1-codex",
        "gpt-5-codex",
        "gpt-5.1-codex-mini",
        "codex-mini-latest",
        "o3",
        "o3-mini",
        "o3-deep-research",
        "o4-mini",
        "o4-mini-deep-research",
    }

    # Declare all instance attributes as fields
    timeout: int = Field(default=120)
    api_base_url: str = Field(default="http://localhost:8000")
    model_enum: Optional[LLMModel] = Field(default=None)
    model_name: str = Field(default="")
    use_codex_route: bool = Field(default=False)
    llm: Optional[Any] = Field(default=None)

    def __init__(
        self,
        model: Optional[LLMModel] = None,
        model_name: Optional[str] = None,
        use_codex_route: Optional[bool] = None,
        api_base_url: str = "http://localhost:8000",
        timeout: int = 120,
        **kwargs
    ):
        """
        Args:
            model: Enum LLMModel pour les modèles LangChain standard
            model_name: Nom du modèle en string (pour Codex/O-series)
            use_codex_route: Force l'utilisation de la route Codex (auto-détecté si None)
            api_base_url: URL de base de l'API (pour la route Codex)
            timeout: Timeout en secondes
            **kwargs: Arguments supplémentaires pour BaseChatModel
        """
        # Initialize parent first with field values
        super().__init__(
            timeout=timeout,
            api_base_url=api_base_url,
            model_enum=None,
            model_name="",
            use_codex_route=False,
            llm=None,
            **kwargs
        )

        # Déterminer le modèle et le mode
        if model is not None:
            # Utilisation d'un modèle LangChain standard via enum
            self.model_enum = model
            self.model_name = model.value
            self.use_codex_route = False
            self.llm = LLMModelFactory.get_llm(model)
        elif model_name is not None:
            # Utilisation d'un nom de modèle custom
            self.model_enum = None
            self.model_name = model_name

            # Auto-détection ou forçage manuel
            if use_codex_route is None:
                self.use_codex_route = model_name in self.CODEX_MODELS
            else:
                self.use_codex_route = use_codex_route

            # Si pas Codex, essayer de créer un LLM LangChain
            if not self.use_codex_route:
                try:
                    # Essayer de trouver l'enum correspondant
                    matching_enum = None
                    for llm_model in LLMModel:
                        if llm_model.value == model_name:
                            matching_enum = llm_model
                            break

                    if matching_enum:
                        self.llm = LLMModelFactory.get_llm(matching_enum)
                    else:
                        raise ValueError(f"Model {model_name} not found in LLMModel enum")
                except Exception as e:
                    raise ValueError(
                        f"Cannot create LangChain LLM for model {model_name}. "
                        f"If this is a Codex/O-series model, set use_codex_route=True. "
                        f"Error: {e}"
                    )
            else:
                self.llm = None
        else:
            raise ValueError("Either 'model' or 'model_name' must be provided")

    @property
    def _llm_type(self) -> str:
        """Type du LLM."""
        if self.use_codex_route:
            return f"universal_codex_{self.model_name}"
        return f"universal_langchain_{self.model_name}"

    @property
    def _identifying_params(self) -> dict:
        """Return identifying parameters for the LLM."""
        return {
            "model_name": self.model_name,
            "use_codex_route": self.use_codex_route,
        }

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Génération synchrone.

        Pour les modèles LangChain, délègue à l'implémentation du modèle sous-jacent.
        Pour Codex, cette méthode ne devrait pas être appelée - utilisez ainvoke() à la place.

        Note: Cette méthode synchrone ne fonctionne pas avec les modèles Codex car ils
        nécessitent des appels HTTP async. Utilisez toujours ainvoke() pour les modèles Codex.
        """
        if not self.use_codex_route:
            # Pour les modèles LangChain, déléguer au LLM sous-jacent
            return self.llm._generate(messages, stop, run_manager, **kwargs)
        else:
            # Pour Codex, lever une erreur claire
            raise RuntimeError(
                f"Cannot use synchronous invoke() with Codex model '{self.model_name}'. "
                f"Codex models require async HTTP calls to OpenAI API. "
                f"Use 'await llm.ainvoke(messages)' instead of 'llm.invoke(messages)'. "
                f"If using in a LangChain chain with JsonOutputParser, call the LLM directly "
                f"instead of using the chain operator (see CourseMaterialGeneratorV2._generate_pedagogical_json for example)."
            )

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Génération asynchrone - route vers Codex ou LangChain selon le modèle.
        """
        if self.use_codex_route:
            return await self._generate_via_codex_route(messages, stop, run_manager, **kwargs)
        else:
            return await self._generate_via_langchain(messages, stop, run_manager, **kwargs)

    async def _generate_via_langchain(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Génération via LangChain standard (Anthropic, Gemini, GPT).
        """
        if hasattr(self.llm, 'ainvoke'):
            # Le LLM supporte les appels async
            result = await self.llm.ainvoke(messages, stop=stop, **kwargs)

            # Convertir en ChatResult si nécessaire
            if isinstance(result, BaseMessage):
                generation = ChatGeneration(message=result)
                return ChatResult(generations=[generation])
            elif isinstance(result, ChatResult):
                return result
            else:
                # Si c'est juste du texte
                ai_message = AIMessage(content=str(result))
                generation = ChatGeneration(message=ai_message)
                return ChatResult(generations=[generation])
        else:
            # Fallback synchrone
            result = self.llm.invoke(messages, stop=stop, **kwargs)

            if isinstance(result, BaseMessage):
                generation = ChatGeneration(message=result)
                return ChatResult(generations=[generation])
            elif isinstance(result, ChatResult):
                return result
            else:
                ai_message = AIMessage(content=str(result))
                generation = ChatGeneration(message=ai_message)
                return ChatResult(generations=[generation])

    async def _generate_via_codex_route(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Génération via l'API OpenAI /v1/responses pour les modèles Codex/O-series.

        Appelle directement l'API OpenAI au lieu de passer par la route interne
        pour éviter les problèmes de connexion en boucle.
        """
        import os

        # Récupérer la clé API OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Convertir les messages LangChain en format API
        messages_dict = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                messages_dict.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                messages_dict.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages_dict.append({"role": "assistant", "content": msg.content})
            else:
                # Fallback pour autres types de messages
                messages_dict.append({"role": "user", "content": str(msg.content)})

        # Préparer la requête pour l'API /v1/responses
        # Note: L'API /v1/responses utilise 'input' au lieu de 'messages'
        payload = {
            "model": self.model_name,
            "input": messages_dict,  # NOT 'messages'
        }

        # Appel direct à l'API OpenAI
        endpoint = "https://api.openai.com/v1/responses"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, json=payload, headers=headers)

            if response.status_code != 200:
                raise ValueError(
                    f"OpenAI API error {response.status_code}: {response.text}"
                )

            result = response.json()

            # L'API /v1/responses retourne un format avec 'output' array
            # qui contient des objets de type 'message' et 'reasoning'
            response_text = None

            if "output" in result:
                # Parcourir l'array output pour trouver le message
                for output_item in result["output"]:
                    if output_item.get("type") == "message":
                        # Extraire le contenu du message
                        content_items = output_item.get("content", [])
                        if content_items and len(content_items) > 0:
                            # Le contenu peut être un dict avec 'text' ou directement du texte
                            first_content = content_items[0]
                            if isinstance(first_content, dict):
                                response_text = first_content.get("text", "")
                            else:
                                response_text = str(first_content)
                        break

            if response_text is None:
                raise ValueError(f"Unexpected response format from OpenAI API: {result}")

            # Convertir la réponse en ChatResult
            ai_message = AIMessage(content=response_text)
            generation = ChatGeneration(message=ai_message)

            return ChatResult(generations=[generation])


# Fonction helper pour créer facilement un UniversalLLM
def create_universal_llm(
    model_identifier: Union[str, LLMModel],
    api_base_url: str = "http://localhost:8000",
    **kwargs
) -> UniversalLLM:
    """
    Helper pour créer un UniversalLLM de manière simple.

    Args:
        model_identifier: Soit un LLMModel enum, soit un string (nom du modèle)
        api_base_url: URL de base pour la route Codex
        **kwargs: Arguments supplémentaires

    Returns:
        Instance de UniversalLLM configurée

    Example:
        # Avec enum (modèle LangChain)
        llm = create_universal_llm(LLMModel.CLAUDE_HAIKU_4_5_20251001)

        # Avec string (auto-détection Codex)
        llm = create_universal_llm("gpt-5.1-codex")

        # Utilisation
        response = llm.invoke("Write a fibonacci function")
    """
    if isinstance(model_identifier, LLMModel):
        return UniversalLLM(model=model_identifier, api_base_url=api_base_url, **kwargs)
    else:
        return UniversalLLM(model_name=model_identifier, api_base_url=api_base_url, **kwargs)
