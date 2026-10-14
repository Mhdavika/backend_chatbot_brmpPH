import unittest
from unittest.mock import patch
from services.chat_service import process_direct_chat

class TestPostManualRefinement(unittest.TestCase):

    @patch("services.chat_service.generate_response")
    def test_ood_natural_tone_groq_zero(self, mock_groq):
        """Out-of-domain queries should return humanized natural rejection without calling Groq."""
        queries = [
            "Siapa gubernur Jawa Barat?",
            "Apa itu karhutla?",
            "Bagaimana cara memasak nasi?",
            "Berapa harga tiket bioskop sekarang?"
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, session_id=f"test-ood-tone-{i}")
                
                # Verify Groq is not called
                mock_groq.assert_not_called()
                
                # Verify friendly/natural rejection tone
                reply = res.get("message", "")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", reply)
                self.assertNotIn("⚠️", reply)
                self.assertNotIn("Daftar topik yang dapat Anda tanyakan:", reply)

    @patch("services.chat_service.generate_response")
    def test_kontak_resmi(self, mock_groq):
        """Contact inquiry should return phone, WA, and official email from KB without Groq."""
        queries = [
            "Bagaimana cara menghubungi BRMP?",
            "Nomor telepon BRMP berapa?",
            "Nomor WhatsApp BRMP berapa?",
            "Apa email BRMP Pengelola Hasil?",
            "Saya mau kontak BRMP"
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, session_id=f"test-kontak-{i}")
                
                mock_groq.assert_not_called()
                
                reply = res.get("message", "")
                self.assertIn("(0251) 8382563", reply)
                self.assertIn("081805503899", reply)
                self.assertIn("brmp.pengelolahasil@pertanian.go.id", reply)

    @patch("services.chat_service.generate_response")
    def test_alamat_dan_lokasi(self, mock_groq):
        """Address/location inquiry should return official address without Groq."""
        queries = [
            "Alamat BRMP Pengelola Hasil di mana?",
            "Dimana kantor BRMP?",
            "Lokasi kantor BRMP Pengelola Hasil",
            "Di mana alamat kantor BRMP?"
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, session_id=f"test-lokasi-{i}")
                
                mock_groq.assert_not_called()
                
                reply = res.get("message", "")
                self.assertIn("Jl. Salak No. 22", reply)
                self.assertIn("16128", reply)

    @patch("services.chat_service.generate_response")
    def test_website_resmi(self, mock_groq):
        """Official website inquiry should return website URL without Groq."""
        queries = [
            "Website resmi BRMP Pengelola Hasil apa?",
            "Apa website resmi BRMP Pengelola Hasil?",
            "Web resmi BRMP Pengelola Hasil?",
            "Situs resmi BRMP Pengelola Hasil apa?"
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, session_id=f"test-website-{i}")
                
                mock_groq.assert_not_called()
                
                reply = res.get("message", "")
                self.assertIn("https://pengelolahasil.brmp.pertanian.go.id/", reply)
                self.assertIn("Website Resmi BRMP Pengelola Hasil", reply)

    @patch("services.chat_service.generate_response")
    def test_pengaduan_channels_and_flow(self, mock_groq):
        """Complaint inquiry should return internal & external channels, steps, and assistance."""
        queries = [
            "Saya mau melakukan pengaduan.",
            "Bagaimana tahapan pengaduannya?",
            "Saya mau mengadu.",
            "Bagaimana cara menyampaikan keluhan layanan?"
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, session_id=f"test-pengaduan-{i}")
                
                mock_groq.assert_not_called()
                
                reply = res.get("message", "")
                # Internal channel
                self.assertIn("Formulir Pengaduan BRMP-PH", reply)
                # External channels
                self.assertIn("SP4N-LAPOR!", reply)
                self.assertIn("WBS Kementerian Pertanian", reply)
                self.assertIn("Dumas Kementerian Pertanian", reply)
                self.assertIn("SIGAP UPG", reply)
                # Steps
                self.assertIn("Tahapan umum pengaduan", reply)
                self.assertIn("Buat Aduan", reply)
                self.assertIn("Buat Laporan", reply)
                self.assertIn("Penyelesaian", reply)

    @patch("services.chat_service.generate_response")
    def test_kerjasama_contact_routing(self, mock_groq):
        """Partnership/cooperation inquiry should return official contact channels."""
        queries = [
            "Saya ingin bekerja sama dengan BRMP.",
            "Bagaimana cara kerja sama dengan BRMP Pengelola Hasil?"
        ]
        for i, q in enumerate(queries):
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, session_id=f"test-kerjasama-{i}")
                
                mock_groq.assert_not_called()
                
                reply = res.get("message", "")
                self.assertIn("081805503899", reply)
                self.assertIn("brmp.pengelolahasil@pertanian.go.id", reply)

if __name__ == "__main__":
    unittest.main()
