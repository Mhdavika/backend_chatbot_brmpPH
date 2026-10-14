import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from services.knowledge_service import (
    search_knowledge,
    get_knowledge_context,
    detect_topics,
    detect_intents,
    is_ambiguous_query,
)
from services.chat_service import (
    process_chat,
    process_direct_chat,
    process_start,
    conversation_sessions,
)


class TestChatbotAIResponse(unittest.TestCase):

    def setUp(self):
        conversation_sessions.clear()

    # =====================================================
    # 1. TOPIC SWITCHING TESTS
    # =====================================================
    def test_topic_switching_retrieval(self):
        print("\n--- TEST: Topic Switching Retrieval ---")

        # Step 1: Paten
        history = [{"role": "user", "content": "Apa itu paten?"}, {"role": "assistant", "content": "Paten adalah hak eksklusif..."}]
        
        # Step 2: Switch to PVT
        res_pvt = search_knowledge("Kalau PVT bagaimana?", history=history)
        self.assertIsNotNone(res_pvt, "PVT knowledge should be found")
        self.assertEqual(res_pvt.get("category"), "pvt", f"Expected category 'pvt', got {res_pvt.get('category')}")
        self.assertIn("pvt", res_pvt.get("id", ""), f"Expected PVT item, got {res_pvt.get('id')}")
        print("  [PASS] Paten -> PVT: Matched ID:", res_pvt.get("id"))

        # Step 3: Switch to Merek
        history.extend([{"role": "user", "content": "Kalau PVT bagaimana?"}, {"role": "assistant", "content": "PVT adalah..."}])
        res_merek = search_knowledge("Kalau merek?", history=history)
        self.assertIsNotNone(res_merek, "Merek knowledge should be found")
        self.assertEqual(res_merek.get("category"), "merek", f"Expected category 'merek', got {res_merek.get('category')}")
        print("  [PASS] PVT -> Merek: Matched ID:", res_merek.get("id"))

        # Step 4: Switch to Hak Cipta
        history.extend([{"role": "user", "content": "Kalau merek?"}, {"role": "assistant", "content": "Merek adalah..."}])
        res_cipta = search_knowledge("Hak cipta itu apa?", history=history)
        self.assertIsNotNone(res_cipta, "Hak Cipta knowledge should be found")
        self.assertEqual(res_cipta.get("category"), "hak_cipta", f"Expected category 'hak_cipta', got {res_cipta.get('category')}")
        print("  [PASS] Merek -> Hak Cipta: Matched ID:", res_cipta.get("id"))

    # =====================================================
    # 2. FOLLOW-UP INTENT TESTS
    # =====================================================
    def test_follow_up_intents(self):
        print("\n--- TEST: Follow-up Intents ---")

        # Skenario Paten -> Persyaratan
        history_paten = [{"role": "user", "content": "Apa itu paten?"}]
        res_syarat_paten = search_knowledge("Apa saja persyaratannya?", history=history_paten)
        self.assertIsNotNone(res_syarat_paten)
        self.assertIn("paten_persyaratan", res_syarat_paten.get("id", ""))
        print("  [PASS] Paten -> Persyaratan: Matched ID:", res_syarat_paten.get("id"))

        # Skenario Paten -> Alur
        res_alur_paten = search_knowledge("Bagaimana alurnya?", history=history_paten)
        self.assertIsNotNone(res_alur_paten)
        self.assertIn("paten_prosedur", res_alur_paten.get("id", ""))
        print("  [PASS] Paten -> Alur: Matched ID:", res_alur_paten.get("id"))

        # Skenario PVT -> Persyaratan
        history_pvt = [{"role": "user", "content": "Saya ingin tahu tentang PVT"}]
        res_syarat_pvt = search_knowledge("Syaratnya apa?", history=history_pvt)
        self.assertIsNotNone(res_syarat_pvt)
        self.assertIn("pvt_persyaratan", res_syarat_pvt.get("id", ""))
        print("  [PASS] PVT -> Persyaratan: Matched ID:", res_syarat_pvt.get("id"))

        # Skenario Merek -> Dokumen
        history_merek = [{"role": "user", "content": "Jelaskan tentang merek"}]
        res_dok_merek = search_knowledge("Dokumen apa yang dibutuhkan?", history=history_merek)
        self.assertIsNotNone(res_dok_merek)
        self.assertTrue("merek_dokumen" in res_dok_merek.get("id", "") or "merek_persyaratan" in res_dok_merek.get("id", ""))
        print("  [PASS] Merek -> Dokumen: Matched ID:", res_dok_merek.get("id"))

        # Skenario Hak Cipta -> Prosedur
        history_cipta = [{"role": "user", "content": "Apa itu hak cipta?"}]
        res_alur_cipta = search_knowledge("Cara daftarnya gimana?", history=history_cipta)
        self.assertIsNotNone(res_alur_cipta)
        self.assertIn("hak_cipta_prosedur", res_alur_cipta.get("id", ""))
        print("  [PASS] Hak Cipta -> Prosedur: Matched ID:", res_alur_cipta.get("id"))

    # =====================================================
    # 3. AMBIGUOUS QUERIES
    # =====================================================
    def test_ambiguous_queries(self):
        print("\n--- TEST: Ambiguous Queries ---")

        # Kasus 1: "gimana?" pada sesi baru (harus minta klarifikasi, tidak tebak paten)
        res_fresh = process_chat(message="gimana?", session_id="test_sess_amb_1", mode="chat")
        self.assertEqual(res_fresh.get("id"), "clarification_response", f"Expected clarification, got {res_fresh}")
        self.assertIn("Maksudnya", res_fresh.get("message", ""))
        print("  [PASS] Fresh session 'gimana?': Clarification triggered, did not guess paten")

        # Kasus 2: "gimana?" setelah topik paten aktif (harus menjawab paten)
        sess_id_2 = "test_sess_amb_2"
        process_chat(message="Apa itu paten?", session_id=sess_id_2, mode="chat")
        res_follow_gimana = process_chat(message="gimana?", session_id=sess_id_2, mode="chat")
        self.assertNotEqual(res_follow_gimana.get("id"), "clarification_response")
        print("  [PASS] Active session Paten -> 'gimana?': Resolved within Paten context")

    # =====================================================
    # 4. SMALL TALK & OUT OF DOMAIN
    # =====================================================
    def test_small_talk_and_ood(self):
        print("\n--- TEST: Small Talk & Out of Domain ---")

        # Halo
        res_greeting = process_chat(message="Halo", session_id="test_sess_st", mode="chat")
        self.assertEqual(res_greeting.get("id"), "natural_response")
        print("  [PASS] Small talk 'Halo'")

        # Terima kasih
        res_thanks = process_chat(message="Terima kasih", session_id="test_sess_st", mode="chat")
        self.assertEqual(res_thanks.get("id"), "natural_response")
        print("  [PASS] Small talk 'Terima kasih'")

        # Kamu suka makan apa?
        res_eat = process_chat(message="Kamu suka makan apa?", session_id="test_sess_st", mode="chat")
        self.assertEqual(res_eat.get("id"), "natural_response")
        self.assertIn("tidak makan", res_eat.get("message", ""))
        print("  [PASS] Small talk 'Kamu suka makan apa?'")

    # =====================================================
    # 5. FLOW MODE REGRESSION
    # =====================================================
    def test_flow_mode_regression(self):
        print("\n--- TEST: Flow Mode Regression ---")

        # Start Flow Mode
        start_res = process_start(session_id="flow_test_1", mode="flow")
        self.assertEqual(start_res.get("mode"), "flow")
        self.assertIn("options", start_res)
        self.assertTrue(len(start_res["options"]) > 0, "Initial node should have options")
        print("  [PASS] Flow Start (Options count:", len(start_res["options"]), ")")

        # Option click in Flow Mode (e.g. Layanan HKI)
        click_res = process_chat(
            current_node_id="root",
            option_id="opt_pengenalan",
            session_id="flow_test_1",
            mode="flow"
        )
        self.assertEqual(click_res.get("mode"), "flow")
        self.assertIsNotNone(click_res.get("id"))
        print("  [PASS] Flow Option Navigation (Node ID:", click_res.get("id"), ")")


    # =====================================================
    # 6. METADATA LEAKAGE PREVENTION TESTS
    # =====================================================
    def test_no_metadata_leak_in_chat_response(self):
        print("\n--- TEST: Anti-Metadata Leakage in Chat Responses ---")
        from unittest.mock import patch, MagicMock

        queries = [
            "Apa itu paten?",
            "Apa itu PVT?",
            "Apa itu merek?",
            "Apa itu hak cipta?",
            "Apa saja persyaratan paten?",
        ]

        forbidden_snippets = [
            "Kategori:",
            "Topik:",
            "(Topik:",
            "Informasi yang tersedia:",
            "Contoh pertanyaan yang berkaitan:",
            "Berikut informasi yang tersedia:",
        ]

        # Case A: Normal or fallback execution
        for q in queries:
            res = process_chat(message=q, session_id="test_leak_1", mode="chat")
            msg = res.get("message", "")
            for snippet in forbidden_snippets:
                self.assertNotIn(
                    snippet,
                    msg,
                    f"Metadata '{snippet}' leaked in response for query '{q}': {msg}"
                )
        print("  [PASS] Direct chat responses do not contain leaked metadata")

        # Case B: Explicit client None fallback
        with patch("services.groq_service.client", None):
            for q in queries:
                res = process_chat(message=q, session_id="test_leak_2", mode="chat")
                msg = res.get("message", "")
                for snippet in forbidden_snippets:
                    self.assertNotIn(
                        snippet,
                        msg,
                        f"Metadata '{snippet}' leaked in fallback (client None) for query '{q}': {msg}"
                    )
        print("  [PASS] Fallback (client is None) does not leak metadata")

        # Case C: Explicit Groq exception (e.g. 429 Rate Limit) fallback
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit reached 429")
        with patch("services.groq_service.client", mock_client):
            for q in queries:
                res = process_chat(message=q, session_id="test_leak_3", mode="chat")
                msg = res.get("message", "")
                for snippet in forbidden_snippets:
                    self.assertNotIn(
                        snippet,
                        msg,
                        f"Metadata '{snippet}' leaked in fallback (429 error) for query '{q}': {msg}"
                    )
        print("  [PASS] Fallback (Groq API exception) does not leak metadata")


if __name__ == "__main__":
    unittest.main(verbosity=2)

