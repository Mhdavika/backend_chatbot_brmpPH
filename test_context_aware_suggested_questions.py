import os
import sys
import unittest
import uuid

sys.path.insert(0, os.path.dirname(__file__))

from services.chat_service import (
    process_chat,
    process_start,
    conversation_sessions,
)
from services.knowledge_service import (
    resolve_suggested_questions,
    STARTER_SUGGESTED_QUESTIONS,
    TOPIC_SUGGESTED_QUESTIONS,
)


class TestContextAwareSuggestedQuestions(unittest.TestCase):

    def setUp(self):
        self.session_id = str(uuid.uuid4())
        conversation_sessions.clear()

    # -------------------------------------------------
    # TEST 1: PVT Fact Found
    # -------------------------------------------------
    def test_01_pvt_fact_found(self):
        """Input 'Apa itu PVT?' -> KB found -> suggestions must be PVT-related."""
        response = process_chat(
            message="Apa itu PVT?",
            session_id=self.session_id,
            mode="chat",
        )
        self.assertIn("suggested_questions", response)
        sq = response["suggested_questions"]
        self.assertTrue(len(sq) > 0, "Suggested questions should not be empty")
        # Check that all suggestions are PVT-related
        for q in sq:
            self.assertTrue(
                "pvt" in q.lower() or "varietas" in q.lower(),
                f"Question '{q}' should be PVT related"
            )

    # -------------------------------------------------
    # TEST 2: PVT Follow-up + KB Miss
    # -------------------------------------------------
    def test_02_pvt_followup_kb_miss(self):
        """Input 1: 'Apa itu PVT?' -> Input 2: 'Bagaimana proses pemeriksaannya?' -> suggestions must stay PVT-related."""
        # Turn 1
        process_chat(
            message="Apa itu PVT?",
            session_id=self.session_id,
            mode="chat",
        )
        # Turn 2 (KB Miss on specific examination stages, but in PVT domain)
        response_2 = process_chat(
            message="Bagaimana proses pemeriksaannya?",
            session_id=self.session_id,
            mode="chat",
        )
        self.assertIn("suggested_questions", response_2)
        sq = response_2["suggested_questions"]
        self.assertTrue(len(sq) > 0, "Suggested questions should not be empty")
        for q in sq:
            self.assertTrue(
                "pvt" in q.lower() or "varietas" in q.lower(),
                f"Follow-up question '{q}' must remain PVT related even when KB fact not found"
            )
        # Must NOT be starter generic questions
        self.assertNotEqual(sq, STARTER_SUGGESTED_QUESTIONS)

    # -------------------------------------------------
    # TEST 3: Patent Follow-up + KB Miss
    # -------------------------------------------------
    def test_03_patent_followup_kb_miss(self):
        """Input 1: 'Apa itu paten?' -> Input 2: 'Bagaimana tahapan pengujian substantif?' -> suggestions stay Patent-related."""
        # Turn 1
        process_chat(
            message="Apa itu paten?",
            session_id=self.session_id,
            mode="chat",
        )
        # Turn 2
        response_2 = process_chat(
            message="Bagaimana tahapan pengujian substantif?",
            session_id=self.session_id,
            mode="chat",
        )
        self.assertIn("suggested_questions", response_2)
        sq = response_2["suggested_questions"]
        self.assertTrue(len(sq) > 0, "Suggested questions should not be empty")
        for q in sq:
            self.assertTrue(
                "paten" in q.lower(),
                f"Follow-up question '{q}' must remain Patent related"
            )
        self.assertNotEqual(sq, STARTER_SUGGESTED_QUESTIONS)

    # -------------------------------------------------
    # TEST 4: Topic Switch (Paten -> Merek)
    # -------------------------------------------------
    def test_04_topic_switch_paten_to_merek(self):
        """Input 1: 'Apa itu paten?' -> Input 2: 'Kalau pendaftaran merek bagaimana?' -> suggestions switch to Merek."""
        # Turn 1: Paten
        process_chat(
            message="Apa itu paten?",
            session_id=self.session_id,
            mode="chat",
        )
        # Turn 2: Switch to Merek
        response_2 = process_chat(
            message="Kalau pendaftaran merek bagaimana?",
            session_id=self.session_id,
            mode="chat",
        )
        self.assertIn("suggested_questions", response_2)
        sq = response_2["suggested_questions"]
        self.assertTrue(len(sq) > 0, "Suggested questions should not be empty")
        for q in sq:
            self.assertTrue(
                "merek" in q.lower() or "merk" in q.lower(),
                f"Switched question '{q}' must be Merek related"
            )

    # -------------------------------------------------
    # TEST 5: New Session
    # -------------------------------------------------
    def test_05_new_session_starter_questions(self):
        """No prior context -> process_start or fresh chat message -> STARTER_SUGGESTED_QUESTIONS."""
        start_response = process_start(
            session_id=self.session_id,
            mode="chat",
        )
        self.assertIn("suggested_questions", start_response)
        self.assertEqual(start_response["suggested_questions"], STARTER_SUGGESTED_QUESTIONS)

    # -------------------------------------------------
    # TEST 6: OOD Interception
    # -------------------------------------------------
    def test_06_ood_interception_safe_suggestions(self):
        """Input: 'Apa itu karhutla?' -> Intercepted by Domain Guard -> Safe generic starter suggestions, no leakage."""
        response = process_chat(
            message="Apa itu karhutla?",
            session_id=self.session_id,
            mode="chat",
        )
        # Verify Domain Guard intercepted
        self.assertIn("BRMP Pengelola Hasil", response["message"])
        self.assertIn("suggested_questions", response)
        # Should be safe starter suggestions
        self.assertEqual(response["suggested_questions"], STARTER_SUGGESTED_QUESTIONS)

    # -------------------------------------------------
    # TEST 7: Deduplication
    # -------------------------------------------------
    def test_07_deduplication(self):
        """Input: 'Apa saja persyaratan paten?' -> suggestions must NOT repeat 'Apa saja persyaratan paten?'."""
        response = process_chat(
            message="Apa saja persyaratan paten?",
            session_id=self.session_id,
            mode="chat",
        )
        sq = response["suggested_questions"]
        for q in sq:
            self.assertNotEqual(
                q.strip().lower(),
                "apa saja persyaratan paten?",
                "Suggested questions must not contain exact replica of user query"
            )
            self.assertTrue("paten" in q.lower())

    # -------------------------------------------------
    # TEST 8: Direct Resolver Generic Fallback
    # -------------------------------------------------
    def test_08_resolver_generic_fallback(self):
        """Topic = None, history = empty -> returns STARTER_SUGGESTED_QUESTIONS."""
        sq = resolve_suggested_questions(
            topic=None,
            current_query=None,
            history=[],
        )
        self.assertEqual(sq, STARTER_SUGGESTED_QUESTIONS)


if __name__ == "__main__":
    unittest.main()
