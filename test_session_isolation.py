import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()

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


class TestSessionIsolationAndUX(unittest.TestCase):

    def setUp(self):
        conversation_sessions.clear()

    # =====================================================
    # TEST A: MEMORY ISOLATION PATEN -> RESET -> SYARAT
    # =====================================================
    def test_memory_isolation_paten_reset(self):
        print("\n--- TEST A: Memory Isolation (Paten -> Reset -> Persyaratan) ---")

        # 1. Old session with Paten
        sess_old = "sess_old_paten_1"
        res1 = process_chat(message="Apa itu paten?", session_id=sess_old, mode="chat")
        self.assertIn("paten", res1.get("message", "").lower())
        print("  [PASS] Sesi Lama (Paten): Bot menjawab tentang Paten")

        # 2. Reset -> New Session ID
        sess_new = "sess_new_paten_2" # Simulasi 'Mulai percakapan baru' dengan session ID baru
        res2 = process_chat(message="Apa saja persyaratannya?", session_id=sess_new, mode="chat")
        
        # Pada sesi baru tanpa konteks, "Apa saja persyaratannya?" tidak memiliki domain topic
        # AI tidak boleh otomatis menganggap ini adalah persyaratan Paten
        context_new = get_knowledge_context(query="Apa saja persyaratannya?", history=[])
        self.assertEqual(context_new, "", "Context harus kosong untuk follow-up tanpa topic di sesi baru")
        print("  [PASS] Sesi Baru (Persyaratan tanpa konteks): Konteks terisolasi bersih, tidak mengasumsikan Paten")

    # =====================================================
    # TEST B: MEMORY ISOLATION PVT -> RESET -> ALUR
    # =====================================================
    def test_memory_isolation_pvt_reset(self):
        print("\n--- TEST B: Memory Isolation (PVT -> Reset -> Alur) ---")

        # 1. Old session with PVT
        sess_old = "sess_old_pvt_1"
        res1 = process_chat(message="Apa itu PVT?", session_id=sess_old, mode="chat")
        self.assertIn("varietas", res1.get("message", "").lower())
        print("  [PASS] Sesi Lama (PVT): Bot menjawab tentang PVT")

        # 2. Reset -> New Session ID
        sess_new = "sess_new_pvt_2"
        context_new = get_knowledge_context(query="Alurnya bagaimana?", history=[])
        self.assertEqual(context_new, "", "Context harus kosong untuk query alur tanpa topic di sesi baru")
        print("  [PASS] Sesi Baru (Alur tanpa konteks): Konteks terisolasi bersih, tidak mengasumsikan PVT")

    # =====================================================
    # TEST C: NEW SESSION BUILDS CONTEXT NORMALLY
    # =====================================================
    def test_new_session_builds_context(self):
        print("\n--- TEST C: New Session Builds Context Normally ---")

        sess_new = "sess_clean_3"
        res1 = process_chat(message="Apa itu Paten?", session_id=sess_new, mode="chat")
        self.assertIn("paten", res1.get("message", "").lower())
        print("  [PASS] Sesi Baru Turn 1: Bot menjawab Paten")

        res2 = process_chat(message="Apa saja persyaratannya?", session_id=sess_new, mode="chat")
        self.assertIn("deskripsi", res2.get("message", "").lower())
        print("  [PASS] Sesi Baru Turn 2: Follow-up di dalam sesi baru berjalan normal mengacu ke Paten")

    # =====================================================
    # TEST D: FLOW MODE IN-PLACE RESET
    # =====================================================
    def test_flow_mode_in_place_reset(self):
        print("\n--- TEST D: Flow Mode In-Place Reset ---")

        # 1. Start Flow Mode
        start_res = process_start(session_id=None, mode="flow")
        self.assertEqual(start_res.get("mode"), "flow")
        self.assertEqual(start_res.get("id"), "main_menu")
        self.assertEqual(len(start_res.get("options", [])), 4)
        sess_flow = start_res.get("session_id")
        print("  [PASS] Flow Start: Initial root node loaded with 4 options (Session:", sess_flow, ")")

        # 2. Navigate deep into flow
        nav_res = process_chat(current_node_id="main_menu", option_id="pengenalan", session_id=sess_flow, mode="flow")
        self.assertEqual(nav_res.get("id"), "pengenalan")
        print("  [PASS] Flow Navigated: Node ID:", nav_res.get("id"))

        # 3. Simulate 'Mulai percakapan baru' in Flow mode -> startChat(null, "flow")
        reset_res = process_start(session_id=None, mode="flow")
        self.assertEqual(reset_res.get("mode"), "flow")
        self.assertEqual(reset_res.get("id"), "main_menu")
        self.assertNotEqual(reset_res.get("session_id"), sess_flow)
        print("  [PASS] Flow In-Place Reset: Kembali ke initial node dengan session ID baru (Session:", reset_res.get("session_id"), ")")

    # =====================================================
    # TEST E: CHAT MODE IN-PLACE RESET
    # =====================================================
    def test_chat_mode_in_place_reset(self):
        print("\n--- TEST E: Chat Mode In-Place Reset ---")

        # 1. Start Chat Mode
        start_res = process_start(session_id=None, mode="chat")
        self.assertEqual(start_res.get("mode"), "chat")
        self.assertEqual(start_res.get("id"), "chat_start")
        sess_chat = start_res.get("session_id")
        print("  [PASS] Chat Start: Initial chat greeting loaded (Session:", sess_chat, ")")

        # 2. Reset Chat Mode -> startChat(null, "chat")
        reset_res = process_start(session_id=None, mode="chat")
        self.assertEqual(reset_res.get("mode"), "chat")
        self.assertEqual(reset_res.get("id"), "chat_start")
        self.assertNotEqual(reset_res.get("session_id"), sess_chat)
        print("  [PASS] Chat In-Place Reset: Kembali ke chat_start dengan session ID baru (Session:", reset_res.get("session_id"), ")")


if __name__ == "__main__":
    unittest.main(verbosity=2)
