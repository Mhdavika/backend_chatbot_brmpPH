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
    process_chat,
    process_direct_chat,
    process_start,
    conversation_sessions,
)


class TestDomainGuardComprehensive(unittest.TestCase):
    """
    Comprehensive Automation Test Suite for BRMP Chatbot Domain Guard & KB-First Architecture.
    Tests exact behavior across all categories A through X.
    """

    def setUp(self):
        conversation_sessions.clear()

    # =========================================================================
    # A. KNOWLEDGE BASE — VALID DEFINITION (A01 - A09)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_a_valid_definitions(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("A01", "Apa itu paten?", "Paten merupakan hak eksklusif"),
            ("A02", "Apa itu PVT?", "Perlindungan Varietas Tanaman"),
            ("A03", "Apa itu merek?", "Merek merupakan tanda yang dapat ditampilkan secara grafis"),
            ("A04", "Apa itu merk?", "Merek merupakan tanda yang dapat ditampilkan secara grafis"),
            ("A05", "Apa itu hak cipta?", "Hak Cipta merupakan hak eksklusif pencipta"),
            ("A06", "Apa pengertian paten?", "Paten merupakan hak eksklusif"),
            ("A07", "Jelaskan PVT?", "Perlindungan Varietas Tanaman"),
            ("A08", "Jelaskan hak cipta?", "Hak Cipta merupakan hak eksklusif pencipta"),
            ("A09", "Jelaskan merek?", "Merek merupakan tanda yang dapat ditampilkan secara grafis"),
        ]

        for tid, query, expected_snippet in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] Groq was called for valid definition: {query}")
                self.assertIn(expected_snippet, res["message"], f"[{tid}] Failed to match KB snippet")
                self.assertNotIn("Kategori:", res["message"])
                self.assertNotIn("MOCK_GROQ_UNEXPECTED", res["message"])

    # =========================================================================
    # B. KNOWLEDGE BASE — BRMP DOMAIN (B01 - B15)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_b_brmp_domain_kb(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("B01", "Apa itu BRMP Pengelola Hasil?"),
            ("B02", "Apa tugas BRMP Pengelola Hasil?"),
            ("B03", "Apa fungsi BRMP Pengelola Hasil?"),
            ("B04", "Apa saja layanan BRMP?"),
            ("B05", "Apakah BRMP melayani petani?"),
            ("B06", "Apakah ada konsultasi pertanian?"),
            ("B07", "Apakah ada pelatihan?"),
            ("B08", "Bagaimana cara menghubungi BRMP?"),
            ("B09", "Di mana lokasi BRMP Pengelola Hasil?"),
            ("B10", "Bagaimana cara mengajukan pengaduan?"),
            ("B11", "Apakah BRMP menerima kerja sama?"),
            ("B12", "Apa program BRMP?"),
            ("B13", "Apa hubungan BRMP dengan petani?"),
            ("B14", "Apa teknologi yang digunakan BRMP?"),
            ("B15", "Bagaimana BRMP membantu pemasaran hasil pertanian?"),
        ]

        for tid, query in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] Expected KB direct answer without Groq for query: {query}")
                self.assertNotIn("MOCK_GROQ_UNEXPECTED", res["message"])
                self.assertGreater(len(res["message"]), 20, f"[{tid}] Response message too short")

    # =========================================================================
    # C. OUT-OF-DOMAIN — GENERAL KNOWLEDGE (C01 - C20)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_c_general_knowledge_ood(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("C01", "Apa itu karhutla?"),
            ("C02", "Apa itu Bitcoin?"),
            ("C03", "Apa itu Ethereum?"),
            ("C04", "Apa itu Python?"),
            ("C05", "Bagaimana cara membuat website?"),
            ("C06", "Bagaimana cara belajar coding?"),
            ("C07", "Siapa presiden sekarang?"),
            ("C08", "Siapa wakil presiden Indonesia?"),
            ("C09", "Apa ibu kota Indonesia?"),
            ("C10", "Berapa 123456 x 789?"),
            ("C11", "Apa itu sepak bola?"),
            ("C12", "Siapa Lionel Messi?"),
            ("C13", "Bagaimana cara memasak nasi?"),
            ("C14", "Apa resep nasi goreng?"),
            ("C15", "Apa itu cryptocurrency?"),
            ("C16", "Bagaimana cara trading?"),
            ("C17", "Apa itu saham?"),
            ("C18", "Apa itu JavaScript?"),
            ("C19", "Bagaimana membuat aplikasi Android?"),
            ("C20", "Apa itu mejeuh euy?"),
        ]

        for tid, query in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] OOD query must not call Groq: {query}")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
                self.assertNotIn("MOCK_GROQ_UNEXPECTED", res["message"])

    # =========================================================================
    # D. OUT-OF-DOMAIN — POLITICS (D01 - D06)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_d_politics_ood(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("D01", "Siapa presiden Indonesia?"),
            ("D02", "Siapa wakil presiden Indonesia?"),
            ("D03", "Siapa menteri pertanian?"),
            ("D04", "Apa partai politik terbesar di Indonesia?"),
            ("D05", "Bagaimana kondisi politik Indonesia?"),
            ("D06", "Siapa calon presiden berikutnya?"),
        ]

        for tid, query in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] Politics OOD must not call Groq: {query}")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
                self.assertNotIn("MOCK_GROQ_UNEXPECTED", res["message"])

    # =========================================================================
    # E. OUT-OF-DOMAIN — CODING / TECHNOLOGY GENERAL (E01 - E08)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_e_coding_tech_ood(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("E01", "Apa itu Python?"),
            ("E02", "Apa itu Laravel?"),
            ("E03", "Bagaimana membuat API FastAPI?"),
            ("E04", "Apa itu React?"),
            ("E05", "Bagaimana membuat aplikasi Flutter?"),
            ("E06", "Bagaimana menggunakan Git?"),
            ("E07", "Apa itu Docker?"),
            ("E08", "Bagaimana deploy Next.js?"),
        ]

        for tid, query in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] Coding OOD must not call Groq: {query}")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

    # =========================================================================
    # F. OUT-OF-DOMAIN — FINANCE / CRYPTO (F01 - F06)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_f_finance_crypto_ood(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("F01", "Apa itu Bitcoin?"),
            ("F02", "Bagaimana cara membeli Bitcoin?"),
            ("F03", "Apa itu saham?"),
            ("F04", "Bagaimana cara investasi?"),
            ("F05", "Apa itu forex?"),
            ("F06", "Bagaimana trading XAUUSD?"),
        ]

        for tid, query in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] Finance OOD must not call Groq: {query}")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

    # =========================================================================
    # G. OUT-OF-DOMAIN — RANDOM / GIBBERISH (G01 - G06)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_g_gibberish_ood(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("G01", "xyzabcxyzabc"),
            ("G02", "asdkjasdkljasd"),
            ("G03", "mejeuh euy"),
            ("G04", "qwertyuiop"),
            ("G05", "123456789"),
            ("G06", "blablablabla"),
        ]

        for tid, query in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] Gibberish OOD must not call Groq: {query}")
                self.assertNotIn("MOCK_GROQ_UNEXPECTED", res["message"])

    # =========================================================================
    # H. IN-DOMAIN BUT KB MISS -> GROQ FALLBACK (H01 - H06)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_h_in_domain_kb_miss(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_IN_DOMAIN_ANSWER"
        test_cases = [
            ("H01", "Bagaimana strategi BRMP Pengelola Hasil menghadapi perubahan teknologi pertanian?", True),
            ("H02", "Bagaimana modernisasi pertanian dapat meningkatkan efisiensi petani?", True),
            ("H03", "Bagaimana BRMP dapat mendukung transformasi digital sektor pertanian?", True),
            ("H04", "Apa tantangan modernisasi hasil pertanian di masa depan?", True),
            ("H05", "Bagaimana pemanfaatan AI dapat membantu pengelolaan hasil pertanian?", True),
            ("H06", "Bagaimana strategi pengembangan pasar hasil pertanian?", False),
        ]

        for tid, query, expect_groq in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                if expect_groq:
                    self.assertEqual(mock_groq.call_count, 1, f"[{tid}] In-domain KB miss must call Groq fallback: {query}")
                    call_args = mock_groq.call_args[1]
                    self.assertEqual(call_args["context"], "")
                    self.assertEqual(res["message"], "MOCK_GROQ_IN_DOMAIN_ANSWER")
                else:
                    self.assertEqual(mock_groq.call_count, 0, f"[{tid}] In-domain KB hit must not call Groq: {query}")
                    self.assertTrue(len(res["message"]) > 0)
                    self.assertIn("pasar", res["message"].lower())

    # =========================================================================
    # I. FOLLOW-UP CONVERSATION (I01 - I04)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_i_followup_progression(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_chains = [
            ("I01", "Apa itu paten?", "Apa saja persyaratannya?", "paten_persyaratan", "Persyaratan permohonan paten"),
            ("I02", "Apa itu PVT?", "Apa saja persyaratannya?", "pvt_persyaratan", "Permohonan hak PVT"),
            ("I03", "Apa itu merek?", "Apa saja persyaratannya?", "merek_persyaratan", "Permohonan pendaftaran merek"),
            ("I04", "Apa itu hak cipta?", "Apa saja persyaratannya?", "hak_cipta_persyaratan", "pencatatan ciptaan"),
        ]

        for tid, q1, q2, exp_id, exp_snippet in test_chains:
            with self.subTest(tid=tid):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                # Turn 1
                res1 = process_direct_chat(q1, session_id)
                self.assertEqual(mock_groq.call_count, 0)

                # Turn 2
                res2 = process_direct_chat(q2, session_id)
                self.assertEqual(mock_groq.call_count, 0)
                self.assertIn(exp_snippet, res2["message"], f"[{tid}] Follow-up failed to match {exp_id}")

    # =========================================================================
    # J. HISTORY MUST NOT LEAK INTO NEW TOPIC (J01 - J03)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_j_history_isolation_from_ood(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("J01", "Apa itu paten?", "Apa itu Bitcoin?"),
            ("J02", "Apa itu PVT?", "Apa itu karhutla?"),
            ("J03", "Apa itu merek?", "Apa itu Python?"),
        ]

        for tid, q1, q2 in test_cases:
            with self.subTest(tid=tid):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                # Turn 1
                process_direct_chat(q1, session_id)
                self.assertEqual(mock_groq.call_count, 0)

                # Turn 2 (OOD must NOT inherit Turn 1 topic)
                res2 = process_direct_chat(q2, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] OOD after history called Groq unexpectedly: {q2}")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res2["message"])

    # =========================================================================
    # K. TOPIC SWITCHING (K01 - K03)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_k_topic_switching(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("K01", ["Apa itu paten?", "Apa itu PVT?", "Apa saja persyaratannya?"], "Permohonan hak PVT"),
            ("K02", ["Apa itu paten?", "Apa itu merek?", "Apa saja persyaratannya?"], "Permohonan pendaftaran merek"),
            ("K03", ["Apa itu PVT?", "Apa itu hak cipta?", "Apa saja persyaratannya?"], "pencatatan ciptaan"),
        ]

        for tid, queries, exp_snippet in test_cases:
            with self.subTest(tid=tid):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                for i, q in enumerate(queries):
                    res = process_direct_chat(q, session_id)
                    self.assertEqual(mock_groq.call_count, 0)
                    if i == len(queries) - 1:
                        self.assertIn(exp_snippet, res["message"], f"[{tid}] Switch failed to land on expected fact")

    # =========================================================================
    # L. GENUINE FOLLOW-UP VS NEW QUESTION (L01 - L04)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_l_followup_vs_new(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        
        # L01: Follow-up requirements
        mock_groq.reset_mock()
        s1 = "session-L01"
        process_direct_chat("Apa itu paten?", s1)
        res_l01 = process_direct_chat("Bagaimana persyaratannya?", s1)
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("Persyaratan permohonan paten", res_l01["message"])

        # L02: New topic OOD
        mock_groq.reset_mock()
        s2 = "session-L02"
        process_direct_chat("Apa itu paten?", s2)
        res_l02 = process_direct_chat("Apa itu Bitcoin?", s2)
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_l02["message"])

        # L03: Follow-up process
        mock_groq.reset_mock()
        s3 = "session-L03"
        process_direct_chat("Apa itu paten?", s3)
        res_l03 = process_direct_chat("Bagaimana prosesnya?", s3)
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("Permohonan paten diajukan melalui layanan resmi DJKI", res_l03["message"])

        # L04: New topic OOD
        mock_groq.reset_mock()
        s4 = "session-L04"
        process_direct_chat("Apa itu paten?", s4)
        res_l04 = process_direct_chat("Siapa presiden sekarang?", s4)
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_l04["message"])

    # =========================================================================
    # M. SMALL TALK / NATURAL RESPONSE (M01 - M06)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_m_small_talk(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("M01", "Halo", "Halo! 👋 Saya asisten informasi BRMP Pengelola Hasil"),
            ("M02", "Hai", "Halo! 👋 Saya asisten informasi BRMP Pengelola Hasil"),
            ("M03", "Selamat pagi", "Halo! 👋 Saya asisten informasi BRMP Pengelola Hasil"),
            ("M04", "Terima kasih", "Sama-sama! 😊"),
            ("M05", "Makasih", "Sama-sama! 😊"),
            ("M06", "kamu siapa", "Saya asisten informasi BRMP Pengelola Hasil"),
        ]

        for tid, query, exp_snippet in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                res = process_direct_chat(query, session_id)
                self.assertEqual(mock_groq.call_count, 0)
                self.assertIn(exp_snippet, res["message"])

    # =========================================================================
    # N. AMBIGUOUS QUERY (N01 - N02)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_n_ambiguous_queries(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        
        # N01: Fresh session ambiguous query -> clarification (Zero-Groq)
        mock_groq.reset_mock()
        s1 = "session-N01"
        res_n01 = process_direct_chat("gimana?", s1)
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("Maksudnya ingin mengetahui bagaimana tentang apa ya?", res_n01["message"])

        # N02: History Paten -> ambiguous follow-up "Syaratnya?" -> paten_persyaratan (Zero-Groq)
        mock_groq.reset_mock()
        s2 = "session-N02"
        process_direct_chat("Apa itu paten?", s2)
        res_n02 = process_direct_chat("Syaratnya?", s2)
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("Persyaratan permohonan paten", res_n02["message"])

    # =========================================================================
    # O. BOUNDARY / FALSE POSITIVE TEST (O01 - O09)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_o_boundary_tests(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_IN_DOMAIN_ANSWER"
        
        # O01 - O05: General technology without agriculture/BRMP anchor -> OOD (Zero-Groq)
        ood_cases = [
            ("O01", "Apa itu teknologi?"),
            ("O02", "Apa itu teknologi blockchain?"),
            ("O03", "Apa itu teknologi AI?"),
            ("O04", "Saya ingin belajar Python untuk membuat aplikasi."),
            ("O05", "Bagaimana cara membuat website?"),
        ]
        for tid, query in ood_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                res = process_direct_chat(query, f"session-{tid}")
                self.assertEqual(mock_groq.call_count, 0)
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

        # O06: In-domain KB hit (teknologi pertanian -> KB item teknologi)
        mock_groq.reset_mock()
        res_o06 = process_direct_chat("Apa itu teknologi pertanian?", "session-O06")
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("teknologi", res_o06["message"].lower())

        # O07 - O09: In-domain questions -> routed to Groq or KB
        mock_groq.reset_mock()
        res_o07 = process_direct_chat("Bagaimana teknologi pertanian membantu petani?", "session-O07")
        self.assertNotIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_o07["message"])

        mock_groq.reset_mock()
        res_o08 = process_direct_chat("Bagaimana modernisasi pertanian dilakukan?", "session-O08")
        self.assertNotIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_o08["message"])

        mock_groq.reset_mock()
        res_o09 = process_direct_chat("Apa peran BRMP dalam modernisasi pertanian?", "session-O09")
        self.assertNotIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_o09["message"])

    # =========================================================================
    # P. HKI BOUNDARY TEST (P01 - P08)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_p_hki_boundaries(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_HKI_ANSWER"
        
        # P01 - P06: In-domain HKI (Must not be blocked by Domain Guard)
        in_domain_hki = [
            ("P01", "Saya ingin mendaftarkan paten."),
            ("P02", "Bagaimana perlindungan varietas tanaman?"),
            ("P03", "Saya ingin melindungi hasil pemuliaan tanaman."),
            ("P04", "Bagaimana mendaftarkan merek?"),
            ("P05", "Bagaimana perlindungan karya cipta?"),
            ("P06", "Bagaimana perlindungan invensi?"),
        ]
        for tid, query in in_domain_hki:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                res = process_direct_chat(query, f"session-{tid}")
                self.assertNotIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

        # P07 - P08: Non-HKI general law -> OOD (Zero-Groq)
        mock_groq.reset_mock()
        res_p07 = process_direct_chat("Bagaimana hukum pidana?", "session-P07")
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_p07["message"])

        mock_groq.reset_mock()
        res_p08 = process_direct_chat("Apa itu hukum perdata?", "session-P08")
        self.assertEqual(mock_groq.call_count, 0)
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res_p08["message"])

    # =========================================================================
    # Q. NEGATIVE HISTORY TEST (Q01)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_q_negative_history_queries(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        ood_queries = [
            ("Q01_1", "Apa itu Bitcoin?"),
            ("Q01_2", "Apa itu Python?"),
            ("Q01_3", "Siapa presiden sekarang?"),
            ("Q01_4", "Apa itu karhutla?"),
            ("Q01_5", "Bagaimana cara memasak nasi?"),
            ("Q01_6", "Apa itu saham?"),
        ]

        for tid, q in ood_queries:
            with self.subTest(tid=tid, query=q):
                mock_groq.reset_mock()
                session_id = f"session-{tid}"
                # Turn 1: Paten
                process_direct_chat("Apa itu paten?", session_id)
                self.assertEqual(mock_groq.call_count, 0)

                # Turn 2: OOD Query
                res = process_direct_chat(q, session_id)
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] Negative history leaked to Groq: {q}")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])
                self.assertNotIn("Paten merupakan hak eksklusif", res["message"])

    # =========================================================================
    # R. GROQ CALL SAFETY TEST (R01 - R04)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_r_groq_call_safety(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_ANSWER"

        # R01: Valid KB definition -> Groq count == 0
        mock_groq.reset_mock()
        process_direct_chat("Apa itu paten?", "session-R01")
        self.assertEqual(mock_groq.call_count, 0)

        # R02: OOD Bitcoin -> Groq count == 0
        mock_groq.reset_mock()
        process_direct_chat("Apa itu Bitcoin?", "session-R02")
        self.assertEqual(mock_groq.call_count, 0)

        # R03: In-domain KB miss strategy -> Groq count == 1
        mock_groq.reset_mock()
        process_direct_chat("Bagaimana strategi BRMP menghadapi teknologi pertanian?", "session-R03")
        self.assertEqual(mock_groq.call_count, 1)

        # R04: OOD Python -> Groq count == 0
        mock_groq.reset_mock()
        process_direct_chat("Apa itu Python?", "session-R04")
        self.assertEqual(mock_groq.call_count, 0)

    # =========================================================================
    # S. NO HALLUCINATION / DOMAIN FALLBACK TEST (S01)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_s_no_hallucination_leakage(self, mock_groq):
        poison_payload = "MOCK_GROQ_RESPONSE_SHOULD_NEVER_APPEAR"
        mock_groq.return_value = poison_payload

        ood_list = [
            "Apa itu Bitcoin?",
            "Apa itu Python?",
            "Siapa presiden sekarang?",
            "Apa itu karhutla?",
            "Apa itu saham?",
        ]

        for q in ood_list:
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, f"session-s-{q}")
                self.assertNotIn(poison_payload, res["message"])
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

    # =========================================================================
    # T. FLOW MODE REGRESSION TEST (T01)
    # =========================================================================

    def test_category_t_flow_mode_regression(self):
        # 1. Flow start
        start_res = process_start(mode="flow")
        self.assertEqual(start_res["mode"], "flow")
        self.assertIn("options", start_res)
        self.assertGreaterEqual(len(start_res["options"]), 2)

        # 2. Flow option click
        session_id = start_res["session_id"]
        chat_res = process_chat(
            current_node_id=start_res["id"],
            option_id=start_res["options"][0]["id"],
            session_id=session_id,
            mode="flow",
        )
        self.assertEqual(chat_res["mode"], "flow")
        self.assertIsNotNone(chat_res["id"])
        self.assertGreater(len(chat_res["message"]), 10)

    # =========================================================================
    # U. SESSION ISOLATION TEST (U01)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_u_session_isolation(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        session_a = "session-iso-A"
        session_b = "session-iso-B"

        # Session A: Paten
        process_direct_chat("Apa itu paten?", session_a)

        # Session B: PVT
        process_direct_chat("Apa itu PVT?", session_b)

        # Session A follow-up: Syarat -> Paten
        res_a = process_direct_chat("Apa saja persyaratannya?", session_a)
        self.assertIn("Persyaratan permohonan paten", res_a["message"])

        # Session B follow-up: Syarat -> PVT
        res_b = process_direct_chat("Apa saja persyaratannya?", session_b)
        self.assertIn("Permohonan hak PVT", res_b["message"])

    # =========================================================================
    # V. NORMALIZATION TEST (V01)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_v_normalization(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        variations = [
            "Apa itu PATEN?",
            "apa itu paten?",
            "  Apa itu paten?  ",
            "APA ITU PATEN",
            "Apa itu MERK?",
            "Apa itu MEREK?",
        ]

        for q in variations:
            with self.subTest(query=q):
                mock_groq.reset_mock()
                res = process_direct_chat(q, f"session-v-{q}")
                self.assertEqual(mock_groq.call_count, 0)
                self.assertNotIn("MOCK_GROQ_UNEXPECTED", res["message"])
                self.assertNotIn("Kategori:", res["message"])

    # =========================================================================
    # W. DOMAIN KEYWORD FALSE POSITIVE (W01 - W05)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_w_keyword_false_positives(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_UNEXPECTED"
        test_cases = [
            ("W01", "Apa program TV malam ini?"),
            ("W02", "Bagaimana teknologi blockchain bekerja?"),
            ("W03", "Bagaimana pasar saham hari ini?"),
            ("W04", "Bagaimana hasil pertandingan sepak bola?"),
            ("W05", "Program Python apa yang bagus?"),
        ]

        for tid, query in test_cases:
            with self.subTest(tid=tid, query=query):
                mock_groq.reset_mock()
                res = process_direct_chat(query, f"session-{tid}")
                self.assertEqual(mock_groq.call_count, 0, f"[{tid}] False positive query called Groq: {query}")
                self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res["message"])

    # =========================================================================
    # X. PROPERTY / INVARIANT TESTS (INV-01 - INV-08)
    # =========================================================================

    @patch("services.chat_service.generate_response")
    def test_category_x_invariants(self, mock_groq):
        mock_groq.return_value = "MOCK_GROQ_ANSWER"

        # INV-01: KB Match -> Groq NOT called
        mock_groq.reset_mock()
        fact = search_knowledge_fact("Apa itu paten?")
        self.assertTrue(fact["fact_found"])
        process_direct_chat("Apa itu paten?", "session-inv-01")
        self.assertEqual(mock_groq.call_count, 0)

        # INV-02: Domain Fallback -> Groq NOT called
        mock_groq.reset_mock()
        process_direct_chat("Apa itu Bitcoin?", "session-inv-02")
        self.assertEqual(mock_groq.call_count, 0)

        # INV-03 & INV-05: Out of domain query -> groq_called = False
        mock_groq.reset_mock()
        self.assertFalse(is_query_in_domain("Apa itu karhutla?"))
        process_direct_chat("Apa itu karhutla?", "session-inv-03")
        self.assertEqual(mock_groq.call_count, 0)

        # INV-06: New unrelated topic -> does NOT inherit active topic
        mock_groq.reset_mock()
        s6 = "session-inv-06"
        process_direct_chat("Apa itu paten?", s6)
        res6 = process_direct_chat("Siapa presiden sekarang?", s6)
        self.assertIn("hanya bisa membantu pertanyaan yang berkaitan dengan BRMP Pengelola Hasil", res6["message"])
        self.assertEqual(mock_groq.call_count, 0)

        # INV-07: Genuine follow-up -> inherits active topic
        mock_groq.reset_mock()
        s7 = "session-inv-07"
        process_direct_chat("Apa itu paten?", s7)
        res7 = process_direct_chat("Apa saja persyaratannya?", s7)
        self.assertIn("Persyaratan permohonan paten", res7["message"])
        self.assertEqual(mock_groq.call_count, 0)

        # INV-08: Explicit topic switch -> overrides previous topic
        mock_groq.reset_mock()
        s8 = "session-inv-08"
        process_direct_chat("Apa itu paten?", s8)
        res8 = process_direct_chat("Apa itu PVT?", s8)
        self.assertIn("Perlindungan Varietas Tanaman", res8["message"])
        self.assertNotIn("invensi", res8["message"].lower())
        self.assertEqual(mock_groq.call_count, 0)


if __name__ == "__main__":
    unittest.main()
