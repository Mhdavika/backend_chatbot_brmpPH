import unittest
import uuid
from unittest.mock import patch

from services.chat_service import (
    process_direct_chat,
    process_start,
    CHAT_MODE,
    conversation_sessions,
)
from services.knowledge_service import (
    search_knowledge_fact,
    is_query_in_domain,
)


class TestRefinementQ1to15AndMultiTurn(unittest.TestCase):
    def setUp(self):
        conversation_sessions.clear()

    # =========================================================================
    # PERTANYAAN MANUAL 1-15 REGRESSION TESTS
    # =========================================================================

    def test_q01_brmp_definition(self):
        """1. Apa itu BRMP Pengelola Hasil?"""
        res = process_direct_chat("Apa itu BRMP Pengelola Hasil?", "sess-q1")
        msg = res.get("message", "")
        self.assertIn("Balai Pengelola Hasil Perakitan dan Modernisasi Pertanian", msg)
        self.assertIn("BRMP Pengelola Hasil", msg)

    def test_q02_tugas_brmp(self):
        """2. Apa tugas BRMP Pengelola Hasil?"""
        res = process_direct_chat("Apa tugas BRMP Pengelola Hasil?", "sess-q2")
        msg = res.get("message", "")
        # Intent tugas harus menjawab tugas utama, bukan daftar 5 fungsi
        self.assertIn("melaksanakan pengelolaan hasil perakitan dan modernisasi pertanian", msg)
        self.assertNotIn("1. Penyusunan rencana", msg)

    def test_q03_fungsi_brmp(self):
        """3. Apa fungsi BRMP Pengelola Hasil?"""
        res = process_direct_chat("Apa fungsi BRMP Pengelola Hasil?", "sess-q3")
        msg = res.get("message", "")
        # Intent fungsi harus menjawab daftar fungsi
        self.assertIn("Penyusunan rencana, program, dan anggaran", msg)
        self.assertIn("Pengelolaan dan valuasi hasil perakitan", msg)
        self.assertIn("Pengelolaan kekayaan intelektual dan alih teknologi", msg)

    def test_q04_kepala_balai(self):
        """4. Siapa Kepala Balai BRMP Pengelola Hasil?"""
        res = process_direct_chat("Siapa Kepala Balai BRMP Pengelola Hasil?", "sess-q4")
        msg = res.get("message", "")
        self.assertIn("Nuning Nugrahani", msg)

    def test_q05_alamat(self):
        """5. Di mana alamat BRMP Pengelola Hasil?"""
        res = process_direct_chat("Di mana alamat BRMP Pengelola Hasil?", "sess-q5")
        msg = res.get("message", "")
        self.assertIn("Jl. Salak No. 22", msg)
        self.assertIn("Bogor", msg)

    def test_q06_kontak(self):
        """6. Bagaimana cara menghubungi BRMP Pengelola Hasil?"""
        res = process_direct_chat("Bagaimana cara menghubungi BRMP Pengelola Hasil?", "sess-q6")
        msg = res.get("message", "")
        self.assertIn("(0251) 8382563", msg)
        self.assertIn("081805503899", msg)
        self.assertIn("brmp.pengelolahasil@pertanian.go.id", msg)

    def test_q07_website(self):
        """7. Apa website resmi BRMP Pengelola Hasil?"""
        res = process_direct_chat("Apa website resmi BRMP Pengelola Hasil?", "sess-q7")
        msg = res.get("message", "")
        self.assertIn("pengelolahasil.brmp.pertanian.go.id", msg)

    def test_q08_layanan_tersedia(self):
        """8. Apa saja layanan yang tersedia di BRMP Pengelola Hasil?"""
        res = process_direct_chat("Apa saja layanan yang tersedia di BRMP Pengelola Hasil?", "sess-q8")
        msg = res.get("message", "")
        self.assertIn("BRMP Pengelola Hasil menyediakan layanan publik dan teknis meliputi", msg)
        self.assertIn("Layanan Informasi, Konsultasi, dan Pendampingan Kekayaan Intelektual", msg)
        self.assertIn("alih teknologi dan lisensi", msg.lower())
        # Tidak boleh misdirected ke profil
        self.assertNotIn("BRMP Pengelola Hasil adalah Unit Pelaksana Teknis", msg)

    def test_q09_melayani_petani(self):
        """9. Apakah BRMP Pengelola Hasil melayani petani?"""
        res = process_direct_chat("Apakah BRMP Pengelola Hasil melayani petani?", "sess-q9")
        msg = res.get("message", "")
        self.assertIn("BRMP Pengelola Hasil memberikan layanan informasi teknologi", msg)
        self.assertIn("bimbingan teknis perakitan hasil pertanian", msg)
        self.assertIn("konsultasi adopsi inovasi bagi petani", msg)

    def test_q10_pengelolaan_hasil(self):
        """10. Apa yang dimaksud dengan pengelolaan hasil perakitan dan modernisasi pertanian?"""
        res = process_direct_chat("Apa yang dimaksud dengan pengelolaan hasil perakitan dan modernisasi pertanian?", "sess-q10")
        msg = res.get("message", "")
        self.assertIn("Pengelolaan hasil perakitan dan modernisasi pertanian adalah rangkaian kegiatan", msg)
        self.assertIn("valuasi, pelindungan kekayaan intelektual", msg)

    def test_q11_pemanfaatan_hasil(self):
        """11. Apa yang dimaksud dengan pemanfaatan hasil perakitan dan modernisasi pertanian?"""
        res = process_direct_chat("Apa yang dimaksud dengan pemanfaatan hasil perakitan dan modernisasi pertanian?", "sess-q11")
        msg = res.get("message", "")
        self.assertIn("Pemanfaatan hasil perakitan dan modernisasi pertanian adalah proses pendayagunaan", msg)
        self.assertIn("alih teknologi, lisensi", msg)

    def test_q12_cara_menggunakan_layanan(self):
        """12. Saya ingin menggunakan layanan BRMP, bagaimana caranya?"""
        res = process_direct_chat("Saya ingin menggunakan layanan BRMP, bagaimana caranya?", "sess-q12")
        msg = res.get("message", "")
        self.assertIn("Untuk memanfaatkan layanan yang tersedia di BRMP Pengelola Hasil", msg)
        self.assertIn("081805503899", msg)
        # Tidak boleh mengarang formulir palsu
        self.assertNotIn("KTP, dokumen pendirian", msg)

    def test_q13_persyaratan_layanan(self):
        """13. Apa saja persyaratan untuk mendapatkan layanan BRMP?"""
        res = process_direct_chat("Apa saja persyaratan untuk mendapatkan layanan BRMP?", "sess-q13")
        msg = res.get("message", "")
        self.assertIn("Persyaratan untuk mendapatkan layanan di BRMP Pengelola Hasil disesuaikan dengan jenis layanan", msg)
        self.assertIn("Layanan Informasi Publik (PPID)", msg)
        # Tidak boleh mengarang dokumen umum
        self.assertNotIn("surat keterangan dinas", msg)

    def test_q14_lisensi_cara(self):
        """14. Saya ingin memanfaatkan hasil teknologi melalui lisensi, bagaimana caranya?"""
        res = process_direct_chat("Saya ingin memanfaatkan hasil teknologi melalui lisensi, bagaimana caranya?", "sess-q14")
        msg = res.get("message", "")
        self.assertIn("Pemanfaatan hasil perakitan dan invensi terdaftar milik BRMP Pengelola Hasil melalui lisensi", msg)
        self.assertIn("Pengajuan Permohonan", msg)
        self.assertIn("perjanjian lisensi", msg.lower())

    def test_q15_lisensi_definisi(self):
        """15. Apa itu lisensi di BRMP Pengelola Hasil?"""
        res = process_direct_chat("Apa itu lisensi di BRMP Pengelola Hasil?", "sess-q15")
        msg = res.get("message", "")
        self.assertIn("Lisensi di BRMP Pengelola Hasil merupakan izin atau hak pemanfaatan", msg)
        self.assertIn("alih teknologi resmi", msg)
        # Tidak boleh misdirected ke profil
        self.assertNotIn("BRMP Pengelola Hasil adalah Unit Pelaksana Teknis", msg)

    # =========================================================================
    # MULTI-TURN CONTEXT TESTS (MT-01, MT-02, MT-03)
    # =========================================================================

    def test_mt_01_lisensi_followup(self):
        """
        Test MT-01:
        Turn 1: Apa itu lisensi?
        Turn 2: Bagaimana cara mendapatkannya? -> dipahami sebagai lisensi
        """
        session_id = str(uuid.uuid4())
        res1 = process_direct_chat("Apa itu lisensi?", session_id)
        self.assertIn("Lisensi di BRMP Pengelola Hasil merupakan izin atau hak pemanfaatan", res1["message"])

        res2 = process_direct_chat("Bagaimana cara mendapatkannya?", session_id)
        msg2 = res2["message"]
        # Harus merujuk ke mekanisme alih teknologi / lisensi
        self.assertIn("lisensi", msg2.lower())
        self.assertTrue(
            "kerja sama" in msg2.lower() or "perjanjian lisensi" in msg2.lower() or "alih teknologi" in msg2.lower()
        )

    def test_mt_02_layanan_petani_followup(self):
        """
        Test MT-02:
        Turn 1: Apa saja layanan BRMP?
        Turn 2: Kalau untuk petani bagaimana? -> mempertahankan konteks layanan untuk petani
        """
        session_id = str(uuid.uuid4())
        res1 = process_direct_chat("Apa saja layanan BRMP?", session_id)
        self.assertIn("BRMP Pengelola Hasil menyediakan layanan publik dan teknis meliputi", res1["message"])

        res2 = process_direct_chat("Kalau untuk petani bagaimana?", session_id)
        msg2 = res2["message"]
        self.assertIn("petani", msg2.lower())
        self.assertTrue(
            "layanan" in msg2.lower() or "konsultasi" in msg2.lower() or "bimbingan teknis" in msg2.lower()
        )

    def test_mt_03_layanan_persyaratan_followup(self):
        """
        Test MT-03:
        Turn 1: Bagaimana cara menggunakan layanan BRMP?
        Turn 2: Apa persyaratannya? -> dipahami sebagai persyaratan layanan BRMP
        """
        session_id = str(uuid.uuid4())
        res1 = process_direct_chat("Bagaimana cara menggunakan layanan BRMP?", session_id)
        self.assertIn("Untuk memanfaatkan layanan yang tersedia di BRMP Pengelola Hasil", res1["message"])

        res2 = process_direct_chat("Apa persyaratannya?", session_id)
        msg2 = res2["message"]
        self.assertIn("persyaratan", msg2.lower())
        self.assertTrue(
            "layanan" in msg2.lower() or "konsultasi" in msg2.lower() or "ppid" in msg2.lower()
        )


if __name__ == "__main__":
    unittest.main()
