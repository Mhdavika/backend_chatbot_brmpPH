import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

from services.knowledge_service import (
    search_knowledge,
    search_knowledge_fact,
    get_clean_kb_answer,
    detect_topics,
    detect_intents,
    normalize_text,
    is_query_in_domain,
)
from services.chat_service import (
    process_direct_chat,
    conversation_sessions,
)


class TestKBFirstArchitecture(unittest.TestCase):

    def setUp(self):
        conversation_sessions.clear()

    # =====================================================
    # 1. DIRECT KB (ZERO-GROQ) TESTS
    # =====================================================

    @patch("services.chat_service.generate_response")
    def test_paten_definition_kb_first(self, mock_generate_response):
        print("\n--- TEST 1: Paten Definition KB-First ---")
        mock_generate_response.return_value = "Groq output should not be used"

        session_id = "test-session-paten-def"
        res = process_direct_chat("Apa itu paten?", session_id)

        # Groq must NOT be called
        mock_generate_response.assert_not_called()
        self.assertEqual(res["mode"], "chat")
        self.assertIn("Paten merupakan hak eksklusif", res["message"])
        self.assertNotIn("Kategori:", res["message"])
        self.assertNotIn("Topik:", res["message"])
        self.assertNotIn("Informasi yang tersedia:", res["message"])
        print("  [PASS] 'Apa itu paten?' answered directly from KB without calling Groq.")

    @patch("services.chat_service.generate_response")
    def test_paten_persyaratan_kb_first(self, mock_generate_response):
        print("\n--- TEST 2: Paten Persyaratan KB-First ---")
        mock_generate_response.return_value = "Groq output should not be used"

        session_id = "test-session-paten-req"
        res = process_direct_chat("Apa saja persyaratan paten?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("Persyaratan permohonan paten mencakup", res["message"])
        self.assertNotIn("Kategori:", res["message"])
        print("  [PASS] 'Apa saja persyaratan paten?' answered directly from KB without calling Groq.")

    @patch("services.chat_service.generate_response")
    def test_merk_and_merek_normalization_kb_first(self, mock_generate_response):
        print("\n--- TEST 3 & 4: 'merk' vs 'merek' Normalization KB-First ---")
        mock_generate_response.return_value = "Groq output should not be used"

        # 3. 'merk'
        session_id_1 = "test-session-merk"
        res_merk = process_direct_chat("Apa itu merk?", session_id_1)
        mock_generate_response.assert_not_called()
        self.assertIn("Merek merupakan tanda yang dapat ditampilkan secara grafis", res_merk["message"])

        # 4. 'merek'
        session_id_2 = "test-session-merek"
        res_merek = process_direct_chat("Apa itu merek?", session_id_2)
        mock_generate_response.assert_not_called()
        self.assertIn("Merek merupakan tanda yang dapat ditampilkan secara grafis", res_merek["message"])

        print("  [PASS] Both 'Apa itu merk?' and 'Apa itu merek?' matched 'merek_umum' directly from KB.")

    @patch("services.chat_service.generate_response")
    def test_hak_cipta_kb_first(self, mock_generate_response):
        print("\n--- TEST 5: Hak Cipta Definition KB-First ---")
        mock_generate_response.return_value = "Groq output should not be used"

        session_id = "test-session-cipta"
        res = process_direct_chat("Apa itu hak cipta?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("Hak Cipta merupakan hak eksklusif pencipta", res["message"])
        print("  [PASS] 'Apa itu hak cipta?' answered directly from KB without calling Groq.")

    @patch("services.chat_service.generate_response")
    def test_pvt_kb_first(self, mock_generate_response):
        print("\n--- TEST 6: PVT Definition KB-First ---")
        mock_generate_response.return_value = "Groq output should not be used"

        session_id = "test-session-pvt"
        res = process_direct_chat("Apa itu PVT?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("Perlindungan Varietas Tanaman", res["message"])
        self.assertIn("PVT", res["message"])
        print("  [PASS] 'Apa itu PVT?' answered directly from KB without calling Groq.")

    # =====================================================
    # 2. IN-DOMAIN KB MISS -> GROQ FALLBACK
    # =====================================================

    @patch("services.chat_service.generate_response")
    def test_biaya_paten_fallback_to_groq(self, mock_generate_response):
        print("\n--- TEST 7: Biaya Paten (In-Domain Topic, Fact NOT Found) ---")
        mock_generate_response.return_value = "Untuk rincian biaya pendaftaran paten, saat ini saya belum memiliki nominal resmi yang terverifikasi."

        session_id = "test-session-biaya"
        res = process_direct_chat("Berapa biaya pendaftaran paten?", session_id)

        # Groq MUST be called because in-domain but 'biaya' is not in KB
        mock_generate_response.assert_called_once()
        call_args = mock_generate_response.call_args[1]
        
        # Context sent to Groq must be empty (NOT paten_umum)
        self.assertEqual(call_args["context"], "", "Unrelated topic context must NOT be sent to Groq")
        self.assertEqual(res["message"], "Untuk rincian biaya pendaftaran paten, saat ini saya belum memiliki nominal resmi yang terverifikasi.")
        print("  [PASS] 'Berapa biaya pendaftaran paten?' correctly routed to Groq fallback with context=''")

    @patch("services.chat_service.generate_response")
    def test_in_domain_strategy_groq_fallback(self, mock_generate_response):
        print("\n--- TEST 7B: In-Domain BRMP Strategy (KB Miss -> Groq Fallback) ---")
        mock_generate_response.return_value = "BRMP Pengelola Hasil memiliki strategi terpadu..."

        session_id = "test-session-strategy"
        res = process_direct_chat("Bagaimana strategi BRMP Pengelola Hasil menghadapi perubahan teknologi pertanian?", session_id)

        # In-domain because it explicitly mentions BRMP and teknologi pertanian
        mock_generate_response.assert_called_once()
        call_args = mock_generate_response.call_args[1]
        self.assertEqual(call_args["context"], "")
        self.assertIn("BRMP", res["message"])
        print("  [PASS] In-domain BRMP strategy question correctly routed to Groq fallback (Groq: True).")

    @patch("services.chat_service.generate_response")
    def test_in_domain_modernisasi_pertanian(self, mock_generate_response):
        print("\n--- TEST 7C: In-Domain Modernisasi Pertanian di BRMP ---")
        mock_generate_response.return_value = "Modernisasi pertanian di BRMP difokuskan pada..."

        session_id = "test-session-modernisasi"
        res = process_direct_chat("Bagaimana modernisasi teknologi pertanian di BRMP?", session_id)

        # In-domain because it has 'pertanian' and 'brmp'
        mock_generate_response.assert_called_once()
        print("  [PASS] 'Bagaimana modernisasi teknologi pertanian di BRMP?' correctly routed to Groq fallback.")

    # =====================================================
    # 3. DOMAIN GUARD: OUT-OF-DOMAIN ZERO-GROQ INTERCEPT
    # =====================================================

    @patch("services.chat_service.generate_response")
    def test_out_of_domain_karhutla_guard(self, mock_generate_response):
        print("\n--- TEST 8A: Out-of-Domain 'Apa itu karhutla?' (Domain Guard) ---")
        session_id = "test-session-karhutla"
        res = process_direct_chat("Apa itu karhutla?", session_id)

        # Groq must NOT be called
        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Apa itu karhutla?' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_out_of_domain_bitcoin_guard(self, mock_generate_response):
        print("\n--- TEST 8B: Out-of-Domain 'Apa itu Bitcoin?' (Domain Guard) ---")
        session_id = "test-session-bitcoin"
        res = process_direct_chat("Apa itu Bitcoin?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Apa itu Bitcoin?' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_out_of_domain_python_guard(self, mock_generate_response):
        print("\n--- TEST 8C: Out-of-Domain 'Apa itu Python?' (Domain Guard) ---")
        session_id = "test-session-python"
        res = process_direct_chat("Apa itu Python?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Apa itu Python?' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_out_of_domain_presiden_guard(self, mock_generate_response):
        print("\n--- TEST 8D: Out-of-Domain 'Siapa presiden sekarang?' (Domain Guard) ---")
        session_id = "test-session-presiden"
        res = process_direct_chat("Siapa presiden sekarang?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Siapa presiden sekarang?' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_out_of_domain_wakil_presiden_guard(self, mock_generate_response):
        print("\n--- TEST 8E: Out-of-Domain 'Siapa wakil presiden Indonesia?' (Domain Guard) ---")
        session_id = "test-session-wapres"
        res = process_direct_chat("Siapa wakil presiden Indonesia?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Siapa wakil presiden Indonesia?' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_out_of_domain_mejeuh_euy_guard(self, mock_generate_response):
        print("\n--- TEST 8F: Out-of-Domain 'Apa itu mejeuh euy?' (Domain Guard) ---")
        session_id = "test-session-mejeuh"
        res = process_direct_chat("Apa itu mejeuh euy?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Apa itu mejeuh euy?' intercepted by Domain Guard (Groq: False).")

    # =====================================================
    # 4. BOUNDARY & FALSE-POSITIVE PREVENTION TESTS
    # =====================================================

    @patch("services.chat_service.generate_response")
    def test_boundary_generic_teknologi(self, mock_generate_response):
        print("\n--- TEST 9A: Boundary Generic 'Apa itu teknologi?' (Domain Guard) ---")
        session_id = "test-session-b-tek"
        res = process_direct_chat("Apa itu teknologi?", session_id)

        # Generic teknologi without agriculture / BRMP context is out-of-domain
        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Apa itu teknologi?' without anchor intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_boundary_blockchain(self, mock_generate_response):
        print("\n--- TEST 9B: Boundary 'Bagaimana teknologi blockchain bekerja?' (Domain Guard) ---")
        session_id = "test-session-b-chain"
        res = process_direct_chat("Bagaimana teknologi blockchain bekerja?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Bagaimana teknologi blockchain bekerja?' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_boundary_belajar_python(self, mock_generate_response):
        print("\n--- TEST 9C: Boundary 'Saya ingin belajar Python.' (Domain Guard) ---")
        session_id = "test-session-b-py"
        res = process_direct_chat("Saya ingin belajar Python.", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Saya ingin belajar Python.' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_boundary_ai_terbaru(self, mock_generate_response):
        print("\n--- TEST 9D: Boundary 'Apa teknologi AI terbaru?' (Domain Guard) ---")
        session_id = "test-session-b-ai"
        res = process_direct_chat("Apa teknologi AI terbaru?", session_id)

        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
        print("  [PASS] 'Apa teknologi AI terbaru?' intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_boundary_teknologi_pertanian_in_domain(self, mock_generate_response):
        print("\n--- TEST 9E: Boundary 'Apa itu teknologi pertanian?' (In-Domain KB) ---")
        session_id = "test-session-b-tek-tani"
        res = process_direct_chat("Apa itu teknologi pertanian?", session_id)

        # Has 'pertanian', matches 'teknologi' in KB
        mock_generate_response.assert_not_called()
        self.assertIn("teknologi", res["message"].lower())
        print("  [PASS] 'Apa itu teknologi pertanian?' correctly recognized as in-domain and answered from KB.")

    # =====================================================
    # 5. HISTORY ISOLATION & FOLLOW-UP TESTS
    # =====================================================

    @patch("services.chat_service.generate_response")
    def test_history_paten_then_bitcoin(self, mock_generate_response):
        print("\n--- TEST 10A: History Paten -> 'Apa itu Bitcoin?' ---")
        session_id = "test-session-hist-btc"

        # Turn 1: Paten (KB)
        res1 = process_direct_chat("Apa itu paten?", session_id)
        mock_generate_response.assert_not_called()
        self.assertIn("Paten", res1["message"])

        # Turn 2: Bitcoin (Domain Guard, must NOT inherit paten)
        res2 = process_direct_chat("Apa itu Bitcoin?", session_id)
        mock_generate_response.assert_not_called()
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res2["message"])
        self.assertNotIn("Paten merupakan hak eksklusif", res2["message"])
        print("  [PASS] 'Apa itu Bitcoin?' after Paten history intercepted by Domain Guard (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_history_paten_then_followup(self, mock_generate_response):
        print("\n--- TEST 10B: History Paten -> 'Apa saja persyaratannya?' ---")
        session_id = "test-session-hist-req"

        # Turn 1: Paten (KB)
        res1 = process_direct_chat("Apa itu paten?", session_id)
        mock_generate_response.assert_not_called()

        # Turn 2: Follow-up (Inherit Paten -> paten_persyaratan)
        res2 = process_direct_chat("Apa saja persyaratannya?", session_id)
        mock_generate_response.assert_not_called()
        self.assertIn("Persyaratan permohonan paten", res2["message"])
        print("  [PASS] Follow-up 'Apa saja persyaratannya?' inherited Paten topic and answered from KB (Groq: False).")

    @patch("services.chat_service.generate_response")
    def test_history_paten_then_pvt_switch(self, mock_generate_response):
        print("\n--- TEST 10C: History Paten -> 'Apa itu PVT?' Topic Switch ---")
        session_id = "test-session-hist-pvt"

        # Turn 1: Paten
        process_direct_chat("Apa itu paten?", session_id)
        mock_generate_response.assert_not_called()

        # Turn 2: PVT (Topic Switch -> pvt_umum)
        res2 = process_direct_chat("Apa itu PVT?", session_id)
        mock_generate_response.assert_not_called()
        self.assertIn("Perlindungan Varietas Tanaman", res2["message"])
        self.assertNotIn("invensi", res2["message"].lower())
        print("  [PASS] Topic switch from Paten to PVT answered from KB PVT (Groq: False).")

    # =====================================================
    # 6. ANTI METADATA LEAKAGE
    # =====================================================

    def test_no_metadata_leakage_all_kb_items(self):
        print("\n--- TEST 11: Anti Metadata Leakage Across Queries ---")
        queries = [
            "Apa itu paten?",
            "Apa saja persyaratan paten?",
            "Apa itu merk?",
            "Apa itu hak cipta?",
            "Apa itu PVT?",
            "Apa profil BRMP?",
            "Apa tugas BRMP?",
            "Apa saja layanan BRMP?",
        ]

        forbidden = [
            "Kategori:",
            "Topik:",
            "Informasi yang tersedia:",
            "Contoh pertanyaan yang berkaitan:",
        ]

        for q in queries:
            fact = search_knowledge_fact(q)
            if fact.get("fact_found"):
                ans = fact.get("answer", "")
                for word in forbidden:
                    self.assertNotIn(word, ans, f"Metadata '{word}' leaked in query: '{q}'")
        print("  [PASS] All KB answers are clean without internal metadata leakage.")


if __name__ == "__main__":
    unittest.main()
