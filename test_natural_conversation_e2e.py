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
)
from services.chat_service import (
    process_chat,
    conversation_sessions,
)


class TestNaturalConversationE2E(unittest.TestCase):

    def setUp(self):
        conversation_sessions.clear()

    def test_general_definitions_retrieval(self):
        print("\n--- 1. GENERAL DEFINITIONS ---")
        queries = [
            ("Apa itu paten?", "paten_umum"),
            ("Apa itu PVT?", "pvt_umum"),
            ("Apa itu merek?", "merek_umum"),
            ("Apa itu hak cipta?", "hak_cipta_umum"),
        ]
        for query, expected_id in queries:
            item = search_knowledge(query)
            self.assertIsNotNone(item, f"Query '{query}' should return knowledge item")
            self.assertEqual(item.get("id"), expected_id, f"Query '{query}' expected '{expected_id}', got '{item.get('id')}'")
            print(f"  [PASS] '{query}' -> Matched: {item.get('id')}")

    def test_topic_switching_kalau_x_bagaimana(self):
        print("\n--- 2. TOPIC SWITCHING & 'KALAU X BAGAIMANA?' ---")
        history = [{"role": "user", "content": "Apa itu paten?"}, {"role": "assistant", "content": "Paten adalah..."}]

        pvt_item = search_knowledge("Kalau PVT bagaimana?", history=history)
        self.assertIsNotNone(pvt_item)
        self.assertEqual(pvt_item.get("id"), "pvt_umum", f"Expected 'pvt_umum', got '{pvt_item.get('id')}'")
        print("  [PASS] 'Kalau PVT bagaimana?' -> Matched: pvt_umum (pengenalan, bukan prosedur)")

        history.extend([{"role": "user", "content": "Kalau PVT bagaimana?"}, {"role": "assistant", "content": "PVT adalah..."}])
        merek_item = search_knowledge("Kalau merek bagaimana?", history=history)
        self.assertIsNotNone(merek_item)
        self.assertEqual(merek_item.get("id"), "merek_umum", f"Expected 'merek_umum', got '{merek_item.get('id')}'")
        print("  [PASS] 'Kalau merek bagaimana?' -> Matched: merek_umum (pengenalan, bukan prosedur)")

        history.extend([{"role": "user", "content": "Kalau merek bagaimana?"}, {"role": "assistant", "content": "Merek adalah..."}])
        cipta_item = search_knowledge("Kalau hak cipta bagaimana?", history=history)
        self.assertEqual(cipta_item.get("id"), "hak_cipta_umum", f"Expected 'hak_cipta_umum', got '{cipta_item.get('id')}'")
        print("  [PASS] 'Kalau hak cipta bagaimana?' -> Matched: hak_cipta_umum (pengenalan, bukan prosedur)")


    def test_follow_up_chain(self):
        print("\n--- 3. FOLLOW-UP PROGRESSION CHAIN ---")
        history = [{"role": "user", "content": "Apa itu PVT?"}, {"role": "assistant", "content": "PVT adalah..."}]

        # 1. Persyaratan
        req_item = search_knowledge("Apa saja persyaratannya?", history=history)
        self.assertIsNotNone(req_item)
        self.assertEqual(req_item.get("id"), "pvt_persyaratan")
        print("  [PASS] Follow-up 1: 'Apa saja persyaratannya?' -> pvt_persyaratan")

        # 2. Dokumen
        history.extend([{"role": "user", "content": "Apa saja persyaratannya?"}, {"role": "assistant", "content": "Persyaratannya..."}])
        doc_item = search_knowledge("Dokumen apa saja yang diperlukan?", history=history)
        self.assertIsNotNone(doc_item)
        self.true = doc_item.get("id") in ["pvt_dokumen", "pvt_persyaratan"]
        print(f"  [PASS] Follow-up 2: 'Dokumen apa saja yang diperlukan?' -> {doc_item.get('id')}")

        # 3. Alur
        history.extend([{"role": "user", "content": "Dokumen apa saja yang diperlukan?"}, {"role": "assistant", "content": "Dokumennya..."}])
        alur_item = search_knowledge("Alurnya bagaimana?", history=history)
        self.assertIsNotNone(alur_item)
        self.assertEqual(alur_item.get("id"), "pvt_prosedur")
        print("  [PASS] Follow-up 3: 'Alurnya bagaimana?' -> pvt_prosedur")


    def test_paten_durations(self):
        print("\n--- 4. PATEN DURATION VS PROCESS DURATION ---")
        
        # Masa berlaku
        item_dur = search_knowledge("Berapa lama paten berlaku?")
        self.assertIsNotNone(item_dur)
        self.assertEqual(item_dur.get("id"), "paten_masa_berlaku")
        self.assertIn("20 tahun", item_dur.get("answer", ""))
        self.assertIn("10 tahun", item_dur.get("answer", ""))
        print("  [PASS] 'Berapa lama paten berlaku?' -> Matched: paten_masa_berlaku (20 thn & 10 thn)")

        item_dur_sederhana = search_knowledge("Berapa lama paten sederhana berlaku?")
        self.assertIsNotNone(item_dur_sederhana)
        self.assertEqual(item_dur_sederhana.get("id"), "paten_masa_berlaku")
        print("  [PASS] 'Berapa lama paten sederhana berlaku?' -> Matched: paten_masa_berlaku")

        # Lama proses
        item_proc = search_knowledge("Berapa lama proses paten?")
        self.assertIsNotNone(item_proc)
        self.assertEqual(item_proc.get("id"), "paten_lama_proses")
        self.assertIn("berbeda dengan masa perlindungan", item_proc.get("answer", ""))
        print("  [PASS] 'Berapa lama proses paten?' -> Matched: paten_lama_proses (proses != masa perlindungan)")


    def test_brmp_role_in_patent(self):
        print("\n--- 5. BRMP ROLE IN PATENT APPLICATION ---")
        item_brmp = search_knowledge("Apakah BRMP menerima pendaftaran paten secara langsung?")
        self.assertIsNotNone(item_brmp)
        self.assertEqual(item_brmp.get("id"), "paten_peran_brmp")
        self.assertIn("jembatan", item_brmp.get("answer", "").lower())
        self.assertIn("djki", item_brmp.get("answer", "").lower())
        print("  [PASS] 'Apakah BRMP menerima pendaftaran paten secara langsung?' -> Matched: paten_peran_brmp (Menjembatani ke DJKI)")


    def test_unavailable_information_handling(self):
        print("\n--- 6. UNAVAILABLE INFORMATION HANDLING ---")
        ctx_biaya = get_knowledge_context("Berapa biaya membuat paten?")
        self.assertNotIn("Rp", ctx_biaya)
        print("  [PASS] 'Berapa biaya membuat paten?' -> Tidak ada angka biaya palsu/mengarang")


if __name__ == '__main__':
    unittest.main(verbosity=2)
