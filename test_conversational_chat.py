import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from services.chat_service import process_direct_chat, process_chat, get_session_history
from services.knowledge_service import search_knowledge_fact, is_query_in_domain

class TestConversationalChat(unittest.TestCase):

    # =========================================================================
    # A. BASIC CONTEXT
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_basic_context_paten_persyaratan(self, mock_groq):
        """Turn 2 'Apa saja persyaratannya?' inherits Patent context from Turn 1."""
        session_id = "test-conv-basic"
        
        # Turn 1
        res1 = process_direct_chat("Apa itu paten?", session_id=session_id)
        mock_groq.assert_not_called()
        self.assertIn("Paten merupakan hak eksklusif", res1["message"])
        
        # Turn 2
        res2 = process_direct_chat("Apa saja persyaratannya?", session_id=session_id)
        mock_groq.assert_not_called()
        self.assertIn("Persyaratan permohonan paten", res2["message"])

    # =========================================================================
    # B. PATEN -> MASA BERLAKU
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_paten_masa_berlaku_followup(self, mock_groq):
        """Turn 2 'Berapa lama masa berlakunya?' inherits Patent context and answers 20 and 10 years."""
        session_id = "test-conv-masa-berlaku"
        
        # Turn 1
        res1 = process_direct_chat("Apa itu paten?", session_id=session_id)
        mock_groq.assert_not_called()
        
        # Turn 2
        res2 = process_direct_chat("Berapa lama masa berlakunya?", session_id=session_id)
        mock_groq.assert_not_called() # KB-first direct hit
        
        reply = res2["message"]
        self.assertIn("20 tahun", reply)
        self.assertIn("10 tahun", reply)
        self.assertIn("paten biasa", reply.lower())

    # =========================================================================
    # C. PATEN -> PROSEDUR
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_paten_prosedur_followup(self, mock_groq):
        """Turn 2 'Bagaimana cara mengajukannya?' inherits Patent context."""
        session_id = "test-conv-prosedur"
        
        process_direct_chat("Apa itu paten?", session_id=session_id)
        mock_groq.reset_mock()
        
        res = process_direct_chat("Bagaimana cara mengajukannya?", session_id=session_id)
        mock_groq.assert_not_called()
        self.assertIn("Permohonan paten diajukan melalui layanan resmi DJKI", res["message"])

    # =========================================================================
    # D. BRMP -> KONTAK ANAPHORIC
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_brmp_kontak_anaphoric(self, mock_groq):
        """Turn 2 'Bagaimana cara menghubunginya?' inherits BRMP context and returns official contact."""
        session_id = "test-conv-kontak"
        
        # Turn 1
        res1 = process_direct_chat("Apa layanan BRMP Pengelola Hasil?", session_id=session_id)
        mock_groq.assert_not_called()
        
        # Turn 2
        res2 = process_direct_chat("Bagaimana cara menghubunginya?", session_id=session_id)
        mock_groq.assert_not_called() # KB-first direct fact
        
        reply = res2["message"]
        self.assertIn("(0251) 8382563", reply)
        self.assertIn("081805503899", reply)
        self.assertIn("brmp.pengelolahasil@pertanian.go.id", reply)

    # =========================================================================
    # E. BRMP -> CONTACT VARIATIONS
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_contact_variations(self, mock_groq):
        """Various contact phrasings consistently return official contact."""
        variations = [
            "Bagaimana cara menghubungi BRMP?",
            "Bagaimana cara menghubunginya?",
            "Bagaimana cara hubungi BRMP?",
            "Nomor WhatsApp BRMP berapa?",
            "Email BRMP Pengelola Hasil apa?",
        ]
        for i, q in enumerate(variations):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, session_id=f"test-var-kontak-{i}")
                mock_groq.assert_not_called()
                reply = res["message"]
                self.assertTrue(
                    "(0251) 8382563" in reply or "081805503899" in reply or "brmp.pengelolahasil@pertanian.go.id" in reply,
                    f"Contact info missing for query: {q}"
                )

    # =========================================================================
    # F. TOPIC SWITCHING (Paten -> PVT -> Persyaratan)
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_topic_switching_paten_to_pvt(self, mock_groq):
        """Topic switch from Patent to PVT must override Patent context on follow-up."""
        session_id = "test-conv-switch"
        
        # Turn 1: Paten
        process_direct_chat("Apa itu paten?", session_id=session_id)
        
        # Turn 2: PVT (Topic switch)
        res2 = process_direct_chat("Apa itu PVT?", session_id=session_id)
        self.assertIn("Perlindungan Varietas Tanaman", res2["message"])
        
        # Turn 3: Follow-up (Should be PVT, not Paten)
        res3 = process_direct_chat("Apa saja persyaratannya?", session_id=session_id)
        mock_groq.assert_not_called()
        self.assertIn("Permohonan hak PVT", res3["message"])
        self.assertNotIn("spesifikasi paten", res3["message"])

    # =========================================================================
    # G. CONTEXT RESET & ISOLATION
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_context_reset_and_isolation(self, mock_groq):
        """Fresh session without prior context must not guess Patent or PVT."""
        # Session A: Paten
        process_direct_chat("Apa itu paten?", session_id="session-A")
        
        # Fresh Session B: Persyaratan without context
        res_fresh = process_direct_chat("Apa saja persyaratannya?", session_id="session-B-fresh")
        mock_groq.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_fresh["message"])

    @patch("services.chat_service.generate_response")
    def test_multi_user_session_isolation(self, mock_groq):
        """Parallel sessions for different users maintain their own respective topics."""
        # Session Paten
        process_direct_chat("Apa itu paten?", session_id="session-user-paten")
        
        # Session PVT
        process_direct_chat("Apa itu PVT?", session_id="session-user-pvt")
        
        # Follow-up on Paten session
        res_paten = process_direct_chat("Apa saja persyaratannya?", session_id="session-user-paten")
        self.assertIn("paten", res_paten["message"].lower())
        
        # Follow-up on PVT session
        res_pvt = process_direct_chat("Apa saja persyaratannya?", session_id="session-user-pvt")
        self.assertIn("pvt", res_pvt["message"].lower())

    # =========================================================================
    # H. OOD AFTER CONTEXT
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_ood_after_context(self, mock_groq):
        """OOD query after in-domain context must still be intercepted by Domain Guard."""
        session_id = "test-conv-ood"
        
        # Turn 1: In-domain
        process_direct_chat("Apa itu paten?", session_id=session_id)
        
        # Turn 2: OOD query
        res = process_direct_chat("Bagaimana cara memasak nasi?", session_id=session_id)
        mock_groq.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

    # =========================================================================
    # I. AMBIGUOUS FOLLOW-UP
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_ambiguous_standalone_vs_followup(self, mock_groq):
        """Standalone 'gimana?' triggers clarification; 'Terus alurnya bagaimana?' inherits topic."""
        # Fresh standalone 'gimana?'
        res_fresh = process_direct_chat("gimana?", session_id="session-fresh-gimana")
        self.assertIn("Maksudnya ingin mengetahui bagaimana tentang apa ya?", res_fresh["message"])
        
        # Follow-up after topic
        session_topic = "session-topic-gimana"
        process_direct_chat("Apa itu paten?", session_id=session_topic)
        res_followup = process_direct_chat("Terus alurnya bagaimana?", session_id=session_topic)
        self.assertIn("Permohonan paten diajukan", res_followup["message"])

    # =========================================================================
    # J. MULTI-TURN BRMP SCENARIO
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_multiturn_brmp_scenario(self, mock_groq):
        """Full 3-turn dialog on BRMP profile -> services -> contact."""
        session_id = "test-multiturn-brmp"
        
        # Turn 1: Profile
        res1 = process_direct_chat("Apa itu BRMP Pengelola Hasil?", session_id=session_id)
        self.assertIn("pengelolaan hasil pertanian", res1["message"])
        
        # Turn 2: Services
        res2 = process_direct_chat("Apa layanan yang tersedia?", session_id=session_id)
        self.assertIn("layanan", res2["message"])
        
        # Turn 3: Contact
        res3 = process_direct_chat("Bagaimana cara menghubunginya?", session_id=session_id)
        self.assertIn("(0251) 8382563", res3["message"])

    # =========================================================================
    # K. OOD PROTECTION ON GENERAL PHRASES
    # =========================================================================
    @patch("services.chat_service.generate_response")
    def test_ood_protection_general_phrases(self, mock_groq):
        """General queries containing 'masa' or 'menghubungi' without BRMP/HKI context are blocked."""
        ood_cases = [
            "Berapa lama masa memasak nasi?",
            "Bagaimana cara menghubungi tukang?",
            "Masa berlaku kartu SIM berapa lama?",
        ]
        for i, q in enumerate(ood_cases):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                self.assertFalse(is_query_in_domain(q))
                res = process_direct_chat(q, session_id=f"test-general-ood-{i}")
                mock_groq.assert_not_called()
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

if __name__ == "__main__":
    unittest.main()
