import random
from pydantic import BaseModel
from typing import Optional, List


class QuizItemDto(BaseModel):
    """Représente un item de quiz existant à modifier."""
    questionJson: Optional[dict] = None
    answersJson: Optional[dict] = None
    explanationJson: Optional[dict] = None
    correctAnswerOrder: Optional[int] = None


class QuizGenerationRequestDto(BaseModel):
    """Corps de la requête de génération de quiz."""
    pedagogical_json: dict
    quiz_items: Optional[List[QuizItemDto]] = None
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None


class QuizOutputItemDto(BaseModel):
    """Représente un item de quiz généré."""
    questionJson: dict
    answersJson: dict
    explanationJson: dict
    correctAnswerOrder: int
    # ID du bloc du plan de quiz dont la question découle (génération depuis plan)
    planBlock: Optional[str] = None
    # HTML par slot ("question", "answer_N", "explanation_N") pour les slots en
    # rendering html (génération HTML directe depuis le plan général)
    slots: Optional[dict] = None


def shuffle_quiz_item_answers(item: "QuizOutputItemDto") -> "QuizOutputItemDto":
    """
    Mélange aléatoirement les réponses d'un item de quiz.

    Le LLM place souvent la bonne réponse en premier. Cette fonction :
    1. Mélange les réponses dans answersJson.content
    2. Réassigne les order (1, 2, 3...) dans leur nouvel ordre
    3. Met à jour correctAnswerOrder pour pointer vers la bonne réponse
    4. Réordonne explanationJson.content pour que les order correspondent
       (order 0 = explication générale, inchangé)
    """
    answers = list(item.answersJson.get("content", []))
    correct_order = item.correctAnswerOrder

    # Trouver la réponse correcte avant le shuffle
    correct_answer = next((a for a in answers if a["order"] == correct_order), None)
    if not correct_answer or len(answers) <= 1:
        return item

    random.shuffle(answers)

    # Réassigner les order séquentiellement et retrouver le nouvel order de la bonne réponse
    new_correct_order = None
    for new_order, answer in enumerate(answers, start=1):
        old_order = answer["order"]
        answer = dict(answer)
        answer["order"] = new_order
        answers[new_order - 1] = answer
        if old_order == correct_order:
            new_correct_order = new_order

    # Reconstruire explanationJson en préservant order 0 et en réordonnant les autres
    explanations = item.explanationJson.get("content", [])
    general_explanation = next((e for e in explanations if e["order"] == 0), None)
    per_answer_explanations = {e["order"]: e for e in explanations if e["order"] != 0}

    new_explanations = []
    if general_explanation:
        new_explanations.append(general_explanation)

    for new_order, answer in enumerate(answers, start=1):
        # Retrouver l'ancienne explication correspondant à cet answer via l'order original
        # answers[new_order-1] a déjà son order mis à jour, on cherche dans per_answer_explanations
        # l'explication dont l'order original = position originale de cette réponse
        # On reconstruit depuis la liste originale d'explications par correspondance de position
        original_answer_order = None
        for orig in item.answersJson.get("content", []):
            if orig.get("text") == answer.get("text"):
                original_answer_order = orig["order"]
                break
        explanation = per_answer_explanations.get(original_answer_order)
        if explanation:
            new_explanations.append({**explanation, "order": new_order})

    new_answers_json = {**item.answersJson, "content": answers}
    new_explanation_json = {**item.explanationJson, "content": new_explanations}

    return QuizOutputItemDto(
        questionJson=item.questionJson,
        answersJson=new_answers_json,
        explanationJson=new_explanation_json,
        correctAnswerOrder=new_correct_order,
        planBlock=item.planBlock,
        slots=item.slots,
    )


class QuizTaskResponse(BaseModel):
    """Réponse immédiate après lancement de la tâche Celery."""
    task_id: str
    status: str = "pending"


class QuizResultResponse(BaseModel):
    """Réponse finale contenant les items de quiz générés."""
    success: bool
    quiz_items: List[QuizOutputItemDto]
