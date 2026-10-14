import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from services.chat_service import process_direct_chat
from services.knowledge_service import search_knowledge_fact

class TestWebsiteOfficialRetrieval(unittest.TestCase):

    @patch("services.chat_service.generate_response")
    def test_website_retrieval_all_variations(self, mock_groq):
        """Website queries in various forms should accurately match 'website' and return official URL without calling Groq."""
        queries = [
            "Website resmi BRMP Pengelola Hasil apa?",
            "Apa website resmi BRMP Pengelola Hasil?",
            "Web resmi BRMP Pengelola Hasil?",
            "Situs resmi BRMP Pengelola Hasil apa?",
            "Apa alamat website BRMP Pengelola Hasil?",
            "Link website BRMP Pengelola Hasil?",
            "Website BRMP Pengelola Hasil?",
            "Situs BRMP Pengelola Hasil?",
            "Apa web resmi BRMP?",
            "Link website BRMP apa?",
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                
                # Check direct KB-first retrieval
                fact = search_knowledge_fact(q)
                self.assertTrue(fact.get("fact_found"), f"Failed fact_found for query: {q}")
                self.assertEqual(fact.get("item", {}).get("id"), "website", f"Wrong item matched for query: {q}")
                
                # Check chat response
                res = process_direct_chat(q, session_id=f"test-web-{i}")
                mock_groq.assert_not_called()
                
                reply = res.get("message", "")
                self.assertIn("https://pengelolahasil.brmp.pertanian.go.id/", reply)
                self.assertIn("Website Resmi BRMP Pengelola Hasil", reply)

    @patch("services.chat_service.generate_response")
    def test_lokasi_retrieval_pure_address(self, mock_groq):
        """Location queries should accurately match 'lokasi' and return physical office address."""
        queries = [
            "Alamat kantor BRMP Pengelola Hasil di mana?",
            "Di mana kantor BRMP Pengelola Hasil?",
            "Lokasi kantor BRMP?",
            "BRMP Pengelola Hasil berada di mana?",
            "Alamat BRMP Pengelola Hasil?",
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                
                fact = search_knowledge_fact(q)
                self.assertTrue(fact.get("fact_found"), f"Failed fact_found for query: {q}")
                self.assertEqual(fact.get("item", {}).get("id"), "lokasi", f"Wrong item matched for query: {q}")
                
                res = process_direct_chat(q, session_id=f"test-lok-{i}")
                mock_groq.assert_not_called()
                
                reply = res.get("message", "")
                self.assertIn("Jl. Salak No. 22", reply)
                self.assertIn("16128", reply)

    @patch("services.chat_service.generate_response")
    def test_profil_regression_protected(self, mock_groq):
        """Profile queries should still match 'profil' and not be misdirected to 'website' or 'lokasi'."""
        queries = [
            "Apa itu BRMP?",
            "Apa itu BRMP Pengelola Hasil?",
            "BRMP Pengelola Hasil itu apa?",
            "Jelaskan tentang BRMP Pengelola Hasil",
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                fact = search_knowledge_fact(q)
                self.assertTrue(fact.get("fact_found"))
                self.assertEqual(fact.get("item", {}).get("id"), "profil")

if __name__ == "__main__":
    unittest.main()
