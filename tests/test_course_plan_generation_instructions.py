import unittest

from app.chains.assessment_plan_generator import (
    _CARD_HTML_BASE_RULES,
    _CARD_PLAN_SYSTEM,
    _QUESTION_HTML_PROMPT,
    _QUESTION_PLAN_SYSTEM,
)
from app.chains.course_plan_generator import (
    _MODIFY_SYSTEM_PROMPT,
    apply_plan_operations,
)


def _detailed_quiz_plan():
    return {
        "kind": "quiz_question_html",
        "sections": [
            {
                "id": "s1",
                "title": "Réponses",
                "slot_group": "answers",
                "blocks": [
                    {
                        "id": "s1.b1",
                        "pedagogical_format": "réponse illustrée",
                        "content": "Une pomme entière",
                        "generation_instructions": (
                            "Utiliser pomme.png centrée, largeur maximale 96 px"
                        ),
                        "rendering": "html",
                        "answer_order": 1,
                        "correct": True,
                        "course_image": "pomme.png",
                        "validated": False,
                    }
                ],
            }
        ],
    }


class GenerationInstructionsTest(unittest.TestCase):
    def test_partial_replace_preserves_detailed_block_metadata(self):
        plan, applied, rejected = apply_plan_operations(
            _detailed_quiz_plan(),
            [
                {
                    "op": "replace",
                    "target": "s1.b1",
                    "block": {"content": "Une pomme avec sa peau"},
                }
            ],
        )

        block = plan["sections"][0]["blocks"][0]
        self.assertEqual(block["content"], "Une pomme avec sa peau")
        self.assertTrue(
            block["generation_instructions"].startswith("Utiliser pomme.png")
        )
        self.assertEqual(block["rendering"], "html")
        self.assertEqual(block["answer_order"], 1)
        self.assertIs(block["correct"], True)
        self.assertEqual(block["course_image"], "pomme.png")
        self.assertEqual(block["id"], "s1.b1")
        self.assertIs(block["validated"], False)
        self.assertEqual(len(applied), 1)
        self.assertEqual(rejected, [])

    def test_partial_replace_can_edit_only_generation_instructions(self):
        plan, _, _ = apply_plan_operations(
            _detailed_quiz_plan(),
            [
                {
                    "op": "replace",
                    "target": "s1.b1",
                    "block": {
                        "generation_instructions": (
                            "Utiliser pomme.png centrée, largeur maximale 64 px"
                        )
                    },
                }
            ],
        )

        block = plan["sections"][0]["blocks"][0]
        self.assertEqual(block["content"], "Une pomme entière")
        self.assertTrue(block["generation_instructions"].endswith("64 px"))

    def test_prompts_generate_edit_and_apply_block_instructions(self):
        self.assertIn("generation_instructions", _QUESTION_PLAN_SYSTEM)
        self.assertIn("generation_instructions", _CARD_PLAN_SYSTEM)
        self.assertIn("generation_instructions", _QUESTION_HTML_PROMPT)
        self.assertIn("generation_instructions", _CARD_HTML_BASE_RULES)
        self.assertIn("generation_instructions", _MODIFY_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
