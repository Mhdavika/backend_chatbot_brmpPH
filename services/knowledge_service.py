import json
import os
import re


# =====================================================
# KNOWLEDGE PATH
# =====================================================

KNOWLEDGE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)
    ),
    "data",
    "knowledge_base.json"
)


# =====================================================
# LOAD KNOWLEDGE
# =====================================================

def load_knowledge():

    try:
        with open(
            KNOWLEDGE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if not isinstance(data, dict):
                return {"knowledge": []}

            knowledge = data.get("knowledge", [])

            if not isinstance(knowledge, list):
                return {"knowledge": []}

            return data

    except FileNotFoundError:
        print("WARNING: knowledge_base.json tidak ditemukan.")
        return {"knowledge": []}

    except json.JSONDecodeError as error:
        print("ERROR: knowledge_base.json tidak valid:", error)
        return {"knowledge": []}


# =====================================================
# NORMALIZE TEXT
# =====================================================

def normalize_text(text: str | None) -> str:

    if not text:
        return ""

    text = str(text).lower()

    replacements = {
        "merk dagang": "merek",
        "merek dagang": "merek",
        "merk jasa": "merek",
        "merek jasa": "merek",
        "merk": "merek",
        "hak paten": "paten",
        "hak pvt": "pvt",
        "perlindungan varietas tanaman": "pvt",
        "perlindungan varietas": "pvt",
        "varietas tanaman": "pvt",
        "karya cipta": "hak cipta",
        "gimana": "bagaimana",
        "gmn": "bagaimana",
        "gmana": "bagaimana",
        "bgmn": "bagaimana",
        "pengen": "ingin",
        "mau": "ingin",
        "ngajuin": "mengajukan",
        "ngajukan": "mengajukan",
        "ajukan": "mengajukan",
        "daftarin": "daftarkan",
        "didaftarin": "didaftarkan",
        "dimana": "di mana",
        "kerjasama": "kerja sama",
        "konsul": "konsultasi",
        "info": "informasi",
        "no telp": "nomor telepon",
        "no telepon": "nomor telepon",
        "kalo": "kalau",
        "syarat2": "persyaratan",
        "syarat-syarat": "persyaratan",
        "dokumen2": "dokumen",
        "dokumen-dokumen": "dokumen",
    }

    for old, new in replacements.items():
        text = re.sub(
            rf"\b{re.escape(old)}\b",
            new,
            text
        )

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =====================================================
# STEMMING / SUFFIX STRIPPING FOR INDONESIAN
# =====================================================

def stem_token(token: str) -> str:
    """
    Menormalkan akhiran umum bahasa Indonesia (-nya, -kan, -an, -lah, -kah)
    terutama untuk istilah pencarian domain dan intent.
    """
    token = token.lower().strip()

    if not token or len(token) <= 3:
        return token

    # Pemetaan khusus kata kunci umum
    special_stems = {
        "persyaratannya": "persyaratan",
        "syaratnya": "syarat",
        "ketentuannya": "ketentuan",
        "dokumennya": "dokumen",
        "berkasnya": "berkas",
        "alurnya": "alur",
        "prosedurnya": "prosedur",
        "caranya": "cara",
        "prosesnya": "proses",
        "tahapannya": "tahap",
        "langkahnya": "langkah",
        "biayanya": "biaya",
        "waktunya": "waktu",
        "lamanya": "lama",
        "fungsinya": "fungsi",
        "maksudnya": "maksud",
        "artinya": "arti",
    }

    if token in special_stems:
        return special_stems[token]

    # Akhiran -nya, -lah, -kah, -pun
    for suffix in ["nya", "lah", "kah", "pun"]:
        if token.endswith(suffix) and len(token) > len(suffix) + 3:
            return token[:-len(suffix)]

    return token


# =====================================================
# TOKENIZE
# =====================================================

def tokenize(text: str) -> set[str]:

    normalized = normalize_text(text)

    if not normalized:
        return set()

    return set(normalized.split())


# =====================================================
# STOPWORDS
# =====================================================

STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "pada",
    "atau", "itu", "ini", "saya", "aku", "kami", "kita", "anda",
    "kamu", "bisa", "kah", "ya", "dong", "nih", "sih", "nya",
    "ada", "punya", "akan", "sudah", "belum", "agar", "dapat",
    "terus", "kalau", "kalo", "jadi", "saja", "aja", "adalah",
    "yaitu", "merupakan", "dalam", "bagi", "oleh", "tentang",
    "apa", "apakah", "siapa", "kapan", "mana", "mengapa", "kenapa",
    "bagaimana", "berapa",
}


# =====================================================
# MEANINGFUL TOKENS
# =====================================================

def meaningful_tokens(text: str) -> set[str]:

    words = tokenize(text)
    meaningful = set()

    for word in words:
        stemmed = stem_token(word)
        if word not in STOPWORDS and len(word) > 2:
            meaningful.add(word)
        if stemmed not in STOPWORDS and len(stemmed) > 2:
            meaningful.add(stemmed)

    return meaningful


# =====================================================
# DOMAIN KEYWORDS & ALIASES
# =====================================================

DOMAIN_KEYWORDS = {
    # HKI
    "paten": {
        "paten",
        "invensi",
        "inventor",
        "dipatenkan",
        "mematenkan",
    },
    "pvt": {
        "pvt",
        "varietas",
        "tanaman",
        "pemulia",
        "pemuliaan",
    },
    "merek": {
        "merek",
        "merk",
        "brand",
        "dagang",
        "jasa",
    },
    "hak_cipta": {
        "cipta",
        "ciptaan",
        "pencipta",
        "copyright",
        "karya",
    },

    # BRMP
    "profil": {
        "profil",
        "kedudukan",
        "pengelolaan hasil",
        "pemanfaatan hasil",
    },
    "tugas": {
        "tugas",
        "bertugas",
        "pekerjaan",
    },
    "fungsi": {
        "fungsi",
        "kewenangan",
    },
    "layanan": {
        "layanan",
        "pelayanan",
        "service",
    },
    "petani": {
        "petani",
        "kelompok tani",
        "usahatani",
    },
    "lisensi": {
        "lisensi",
        "royalti",
        "alih teknologi",
        "perjanjian lisensi",
    },
    "konsultasi": {
        "konsultasi",
        "konsul",
        "bertanya",
    },
    "pelatihan": {
        "pelatihan",
        "pendidikan",
        "training",
    },
    "program": {
        "program",
        "kegiatan",
        "agenda",
    },
    "pasar": {
        "pasar",
        "pemasaran",
        "produk",
    },
    "teknologi": {
        "teknologi",
        "teknis",
    },
    "kerjasama": {
        "kemitraan",
        "mitra",
        "kerjasama",
        "kerja sama",
    },
    "kontak": {
        "kontak",
        "hubungi",
        "menghubungi",
        "telepon",
        "email",
        "whatsapp",
        "wa",
    },
    "lokasi": {
        "lokasi",
        "kantor",
        "alamat",
    },
    "website": {
        "website",
        "web",
        "situs",
        "url",
        "link",
        "portal",
        "homepage",
    },
    "pengaduan": {
        "pengaduan",
        "aduan",
        "keluhan",
        "lapor",
        "laporan",
        "mengadu",
    },
}

KEYWORD_ALIASES = {
    "paten": [
        "paten",
        "hak paten",
        "pengajuan paten",
        "pendaftaran paten",
        "permohonan paten",
        "mematenkan",
        "dipatenkan",
        "invensi",
    ],
    "pvt": [
        "pvt",
        "hak pvt",
        "perlindungan varietas tanaman",
        "perlindungan varietas",
        "varietas tanaman",
        "varietas",
        "pemulia",
        "pemuliaan tanaman",
    ],
    "merek": [
        "merek",
        "merk",
        "merek dagang",
        "merk dagang",
        "merek jasa",
        "merk jasa",
        "pendaftaran merek",
        "pengajuan merek",
        "brand",
    ],
    "hak_cipta": [
        "hak cipta",
        "copyright",
        "ciptaan",
        "pencipta",
        "karya cipta",
        "pencatatan hak cipta",
        "pencatatan ciptaan",
    ],
    "profil": [
        "profil brmp",
        "tentang brmp",
        "apa itu brmp",
        "apa itu brmp pengelola hasil",
        "brmp pengelola hasil itu apa",
        "brmp itu apa",
        "kedudukan brmp",
        "kedudukan brmp pengelola hasil",
        "apa itu balai pengelola hasil",
        "pengelolaan hasil",
        "pemanfaatan hasil",
        "pengelolaan hasil perakitan",
        "pemanfaatan hasil perakitan",
        "pengelolaan hasil perakitan dan modernisasi pertanian",
        "pemanfaatan hasil perakitan dan modernisasi pertanian",
    ],
    "tugas": [
        "tugas brmp",
        "apa tugas brmp",
        "tugas brmp pengelola hasil",
        "apa tugas brmp pengelola hasil",
        "bertugas apa",
        "brmp bertugas apa",
        "tugas pokok brmp",
        "tugas utama brmp",
        "mengurus apa",
        "apa yang dilakukan brmp",
    ],
    "fungsi": [
        "fungsi brmp",
        "apa fungsi brmp",
        "fungsi brmp pengelola hasil",
        "apa fungsi brmp pengelola hasil",
        "apa saja fungsi brmp",
        "fungsi balai",
        "apa fungsi balai",
    ],
    "layanan": [
        "layanan brmp",
        "layanan yang tersedia",
        "apa layanan brmp",
        "apa saja layanan yang tersedia di brmp pengelola hasil",
        "apa saja layanan yang tersedia di brmp",
        "layanan yang tersedia di brmp pengelola hasil",
        "apa saja layanan brmp",
        "layanan di brmp",
        "katalog layanan brmp",
        "bentuk layanan brmp",
        "cara menggunakan layanan brmp",
        "persyaratan layanan brmp",
    ],
    "petani": [
        "layanan petani",
        "bantuan petani",
        "untuk petani",
        "petani mendapatkan",
        "melayani petani",
        "hubungan brmp dengan petani",
        "brmp dengan petani",
        "apakah brmp melayani petani",
        "apakah brmp melayani petani?",
        "apakah petani bisa mendapatkan layanan",
        "apakah brmp memberikan layanan kepada petani",
        "kalau untuk petani bagaimana",
        "kalau untuk petani",
    ],
    "lisensi": [
        "lisensi",
        "lisensi brmp",
        "lisensi teknologi",
        "mekanisme lisensi",
        "cara lisensi",
        "perjanjian lisensi",
        "alih teknologi",
        "lisensi teknologi brmp",
        "pemanfaatan melalui lisensi",
        "lisensi hasil penelitian",
        "apa itu lisensi",
        "apa itu lisensi di brmp",
        "apa itu lisensi di brmp pengelola hasil",
        "memanfaatkan hasil teknologi melalui lisensi",
    ],
    "konsultasi": [
        "konsultasi",
        "konsul",
        "mau konsultasi",
        "ingin konsultasi",
    ],
    "pelatihan": [
        "pelatihan",
        "training",
        "pelatihan petani",
    ],
    "program": [
        "program brmp",
        "kegiatan brmp",
    ],
    "pasar": [
        "pasar hasil pertanian",
        "pemasaran",
        "pasar pertanian",
    ],
    "teknologi": [
        "teknologi pertanian",
        "informasi teknologi",
        "teknologi brmp",
        "teknologi yang digunakan brmp",
        "teknologi yang digunakan",
    ],
    "kerjasama": [
        "kerja sama",
        "kerjasama",
        "kemitraan",
        "mitra",
        "menerima kerja sama",
        "menerima kerjasama",
        "membuka kerja sama",
        "bekerja sama",
        "bisa bekerja sama",
        "ingin kerja sama",
        "mengajukan kerja sama",
        "kerja sama dengan brmp",
    ],
    "kontak": [
        "kontak",
        "nomor telepon",
        "nomor telepon brmp",
        "nomor whatsapp",
        "nomor wa",
        "whatsapp brmp",
        "wa brmp",
        "whatsapp",
        "wa",
        "nomor brmp",
        "telepon",
        "email",
        "email brmp",
        "email brmp pengelola hasil",
        "hubungi",
        "menghubungi",
        "menghubunginya",
        "cara menghubungi",
        "cara menghubunginya",
        "cara menghubungi brmp",
        "bagaimana cara menghubunginya",
    ],
    "lokasi": [
        "lokasi",
        "alamat",
        "kantor",
        "di mana kantor",
        "alamat brmp",
        "alamat kantor brmp",
        "lokasi brmp",
        "lokasi kantor brmp",
        "kantor brmp",
        "kantor brmp di mana",
        "brmp di mana",
        "brmp pengelola hasil di mana",
        "dimana kantor brmp",
        "kantor brmp pengelola hasil",
        "di mana kantor brmp pengelola hasil",
        "dimana kantor brmp pengelola hasil",
        "lokasi brmp pengelola hasil",
        "alamat brmp pengelola hasil",
        "brmp pengelola hasil berada di mana",
        "brmp pengelola hasil berlokasi di mana",
    ],
    "website": [
        "website",
        "website brmp",
        "website resmi",
        "website resmi brmp",
        "website brmp pengelola hasil",
        "website resmi brmp pengelola hasil",
        "web brmp",
        "web resmi",
        "web resmi brmp",
        "web resmi brmp pengelola hasil",
        "web brmp pengelola hasil",
        "situs brmp",
        "situs brmp pengelola hasil",
        "situs resmi",
        "situs resmi brmp",
        "situs resmi brmp pengelola hasil",
        "alamat website",
        "alamat website brmp",
        "link website",
        "link website brmp",
        "link website brmp pengelola hasil",
        "url brmp",
        "portal brmp",
    ],
    "pengaduan": [
        "pengaduan",
        "aduan",
        "keluhan",
        "laporan",
        "mengajukan pengaduan",
        "cara mengajukan pengaduan",
        "pengaduan brmp",
        "mengadu",
        "mau mengadu",
        "saya mau mengadu",
        "sampaikan keluhan",
        "menyampaikan keluhan",
        "sampaikan pengaduan",
        "menyampaikan pengaduan",
        "lapor keluhan",
        "tahapan pengaduan",
        "alur pengaduan",
        "prosedur pengaduan",
    ],
}


# =====================================================
# INTENT PATTERNS
# =====================================================

INTENT_KEYWORDS = {
    "persyaratan": [
        "syarat",
        "persyaratan",
        "ketentuan",
        "kriteria",
        "syaratnya",
        "persyaratannya",
        "ketentuannya",
        "apa yang harus disiapkan",
        "apa yang dibutuhkan",
    ],
    "dokumen": [
        "dokumen",
        "dokumennya",
        "berkas",
        "berkasnya",
        "kelengkapan",
        "formulir",
        "surat pernyataan",
        "surat kuasa",
        "deskripsi invensi",
        "klaim",
        "abstrak",
        "label merek",
        "ktp",
    ],
    "prosedur": [
        "cara",
        "caranya",
        "bagaimana cara",
        "prosedur",
        "prosedurnya",
        "alur",
        "alurnya",
        "langkah",
        "langkahnya",
        "tahap",
        "tahapan",
        "tahapannya",
        "proses",
        "prosesnya",
        "mengurus",
        "mendaftar",
        "mendaftarkan",
        "mengajukan",
        "pencatatan",
    ],
    "definisi": [
        "apa itu",
        "apa pengertian",
        "pengertian",
        "definisi",
        "jelaskan",
        "apa yang dimaksud",
        "apa fungsinya",
        "fungsinya apa",
        "fungsi",
    ],
    "kelayakan_penelitian": [
        "hasil penelitian",
        "hasil riset",
        "bisa dipatenkan",
        "bisa didaftarkan",
        "bisa dilindungi",
        "dapat dipatenkan",
        "penelitian saya",
        "inovasi bisa",
        "varietas hasil",
    ],
    "penolakan": [
        "ditolak",
        "alasan ditolak",
        "kenapa ditolak",
        "penolakan",
        "tidak bisa didaftarkan",
        "dilarang",
    ],
    "karya_ciptaan": [
        "karya apa",
        "apa saja yang dilindungi",
        "foto",
        "tulisan",
        "buku",
        "musik",
        "software",
        "video",
        "karya seni",
    ],
    "biaya": [
        "biaya",
        "biayanya",
        "tarif",
        "tarifnya",
        "bayar",
        "bayarnya",
        "pembayaran",
        "biaya pendaftaran",
        "biaya membuat",
        "biaya mengajukan",
        "gratis",
    ],
    "durasi_masa_berlaku": [
        "berapa lama",
        "durasi",
        "jangka waktu",
        "waktunya",
        "lama proses",
        "masa berlaku",
        "berlaku berapa lama",
        "lama perlindungan",
        "masa perlindungan",
        "berapa tahun",
    ],
}


# =====================================================
# DETECT TOPICS
# =====================================================

def detect_topics(query: str) -> set[str]:

    normalized = normalize_text(query)

    if not normalized:
        return set()

    tokens = meaningful_tokens(normalized)
    detected = set()

    # Match aliases with regex word boundary
    for topic, aliases in KEYWORD_ALIASES.items():
        for alias in aliases:
            alias_normalized = normalize_text(alias)
            pattern = rf"(?<!\w){re.escape(alias_normalized)}(?!\w)"
            if re.search(pattern, normalized):
                detected.add(topic)
                break

    # Match domain keywords tokens
    for topic, keywords in DOMAIN_KEYWORDS.items():
        normalized_keywords = {
            normalize_text(keyword)
            for keyword in keywords
        }
        if tokens & normalized_keywords:
            detected.add(topic)

    return detected


# =====================================================
# DETECT INTENTS
# =====================================================

def detect_intents(query: str) -> set[str]:

    normalized = normalize_text(query)

    if not normalized:
        return set()

    detected_intents = set()

    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            kw_norm = normalize_text(kw)
            pattern = rf"(?<!\w){re.escape(kw_norm)}(?!\w)"
            if re.search(pattern, normalized):
                detected_intents.add(intent)
                break

    return detected_intents


# =====================================================
# DETECT HISTORY TOPICS & PRIMARY HISTORY TOPIC
# =====================================================

def detect_history_topics(
    history: list[dict[str, str]] | None = None
) -> set[str]:

    if not history:
        return set()

    detected_topics = set()

    for message in history:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", "")).lower().strip()
        if role != "user":
            continue
        content = message.get("content", "")
        if not content:
            continue
        detected_topics.update(detect_topics(content))

    return detected_topics


def get_primary_history_topic(
    history: list[dict[str, str]] | None = None
) -> str | None:

    if not history:
        return None

    for message in reversed(history):
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", "")).lower().strip()
        if role != "user":
            continue
        content = message.get("content", "")
        if not content:
            continue
        topics = detect_topics(content)
        if topics:
            # Utamakan topik HKI jika ada
            hki_topics = [t for t in ["paten", "pvt", "merek", "hak_cipta"] if t in topics]
            if hki_topics:
                return hki_topics[0]
            specific_topics = [t for t in topics if t != "profil"]
            if specific_topics:
                return sorted(specific_topics)[0]
            return sorted(topics)[0]

    return None


# =====================================================
# AMBIGUOUS QUERY CHECK
# =====================================================

AMBIGUOUS_STANDALONE_WORDS = {
    "gimana",
    "bagaimana",
    "bgmn",
    "gmn",
    "terus",
    "lanjut",
    "lalu",
    "selanjutnya",
    "apa",
    "apaan",
    "knp",
    "kenapa",
    "mengapa",
}

def is_ambiguous_query(query: str) -> bool:
    """
    Mengecek apakah query terlalu singkat/ambigu untuk dijawab tanpa konteks topik sebelumnya.
    """
    normalized = normalize_text(query)
    words = normalized.split()

    if not words:
        return True

    # Jika hanya terdiri dari 1-2 kata dan seluruhnya adalah kata ambigu
    if len(words) <= 2 and all(w in AMBIGUOUS_STANDALONE_WORDS for w in words):
        return True

    return False


# =====================================================
# BUILD SEARCHABLE TEXT
# =====================================================

def build_searchable_text(item: dict) -> str:

    questions = item.get("questions", [])
    category = item.get("category", "")
    item_id = item.get("id", "")
    answer = item.get("answer", "")

    text_parts = [str(item_id), str(category)]

    if isinstance(questions, list):
        text_parts.extend(str(q) for q in questions)

    text_parts.append(str(answer))

    return " ".join(text_parts)


# =====================================================
# SCORE QUESTION
# =====================================================

def score_question(
    query: str,
    question: str,
    query_tokens: set[str],
) -> int:

    question_normalized = normalize_text(question)
    question_tokens = meaningful_tokens(question_normalized)

    score = 0

    if query == question_normalized:
        score += 100
    elif query in question_normalized and len(query) > 5:
        score += 40
    elif question_normalized in query and len(question_normalized) > 5:
        overlap_ratio = len(query_tokens & question_tokens) / len(query_tokens) if query_tokens else 0
        if overlap_ratio >= 0.6:
            score += 35
        else:
            score += 10

    matched = query_tokens & question_tokens
    score += len(matched) * 10

    if query_tokens:
        overlap_ratio = len(matched) / len(query_tokens)
        if overlap_ratio >= 0.75:
            score += 30
        elif overlap_ratio >= 0.5:
            score += 18
        elif overlap_ratio >= 0.3:
            score += 8

    return score


# =====================================================
# FOLLOW-UP DETECTION
# =====================================================

GENUINE_ANAPHORIC_TOKENS = {
    "prosesnya",
    "caranya",
    "syaratnya",
    "persyaratannya",
    "dokumennya",
    "berkasnya",
    "tahapannya",
    "tahapnya",
    "langkahnya",
    "biayanya",
    "waktunya",
    "ketentuannya",
    "alurnya",
    "fungsinya",
    "karyanya",
    "prosedurnya",
    "lamanya",
    "tarifnya",
    "bayarnya",
    "daftarnya",
    "pendaftarannya",
    "pengajuannya",
    "pencatatannya",
    "pengurusannya",
    "permohonannya",
    "urusnya",
    "berlakunya",
    "menghubunginya",
    "mendapatkannya",
    "memperolehnya",
    "menggunakannya",
    "memanfaatkannya",
    "mengaksesnya",
    "mengurusnya",
}

FOLLOW_UP_TRANSITIONS = {
    "selanjutnya",
    "tahap berikutnya",
    "langkah selanjutnya",
    "lalu bagaimana",
    "terus bagaimana",
    "lanjutannya",
    "kemudian bagaimana",
    "terus gimana",
    "lalu gimana",
    "lanjut",
    "terus",
    "kalau untuk petani bagaimana",
    "kalau untuk petani",
    "untuk petani bagaimana",
    "kalau petani bagaimana",
    "bagaimana cara mendapatkannya",
    "bagaimana mendapatkannya",
    "cara mendapatkannya",
}

INQUIRY_AND_OPERATIONAL_TOKENS = {
    "apa", "bagaimana", "berapa", "apakah", "gimana", "bgmn", "gmn",
    "syarat", "persyaratan", "ketentuan", "kriteria", "dokumen", "berkas",
    "formulir", "kelengkapan", "prosedur", "alur", "langkah", "tahap",
    "tahapan", "proses", "cara", "mengurus", "mendaftar", "mendaftarkan",
    "pendaftaran", "daftar", "daftarnya", "pendaftarannya", "mengajukan",
    "pengajuan", "pengajuannya", "pencatatan", "pencatatannya", "mencatatkan",
    "permohonan", "permohonannya", "pemohon", "urus", "pengurusan",
    "definisi", "pengertian", "maksud", "fungsi", "arti", "penelitian",
    "riset", "hasil", "inovasi", "invensi", "varietas", "ciptaan", "karya",
    "biaya", "tarif", "bayar", "pembayaran", "gratis", "durasi",
    "lama", "waktu", "jangka", "tahun", "bulan", "hari", "berlaku", "berlakunya", "masa",
    "perlindungan", "dilindungi", "didaftarkan", "dipatenkan", "bisa",
    "dapat", "diperlukan", "dibutuhkan", "disiapkan", "ada", "saja",
    "secara", "online", "resmi", "layanan", "bantuan", "konsultasi",
    "pelatihan", "informasi", "kantor", "alamat", "kontak", "pengaduan",
    "hubungi", "menghubungi", "menghubunginya", "mendapatkan", "memperoleh",
    "menggunakan", "memanfaatkan", "mengakses", "mendapatkannya", "memperolehnya",
    "menggunakannya", "memanfaatkannya", "mengaksesnya", "petani",
}


def is_follow_up_query(query: str) -> bool:
    """
    Mengecek apakah query merupakan pertanyaan lanjutan (follow-up)
    yang sah untuk mewarisi topik dari riwayat percakapan.

    Prinsip Semantik:
    1. Anaphoric reference (menggunakan akhiran -nya seperti 'prosesnya', 'syaratnya')
       adalah bukti kuat adanya rujukan ke topik sebelumnya.
    2. Frasa transisi seperti 'selanjutnya', 'tahap berikutnya' merujuk konteks sebelumnya.
    3. Jika query membawa subjek/predikat baru di luar domain (misal 'memasak nasi', 'membuat kopi'),
       query adalah subjek baru (NEW TOPIC / OOD), BUKAN follow-up.
    """
    normalized = normalize_text(query)
    if not normalized:
        return False

    intents = detect_intents(normalized)
    topics = detect_topics(normalized)

    # 1. Jika mengandung anaphoric reference eksplisit
    tokens_raw = set(normalized.split())
    if tokens_raw & GENUINE_ANAPHORIC_TOKENS:
        return True

    # 2. Jika mengandung frasa transisi percakapan
    for transition in FOLLOW_UP_TRANSITIONS:
        if transition in normalized:
            return True

    # 3. Pertanyaan definisi tanpa anaphoric reference adalah subjek baru
    if "definisi" in intents:
        return False

    # 4. Cek apakah ada predikat / objek eksternal di luar inquiry & domain tokens
    words = meaningful_tokens(normalized)
    external_tokens = {
        w for w in words
        if w not in INQUIRY_AND_OPERATIONAL_TOKENS
        and stem_token(w) not in INQUIRY_AND_OPERATIONAL_TOKENS
        and w not in CORE_DOMAIN_ANCHORS
    }

    # Jika query membawa kata benda/kerja mandiri di luar domain (misal 'memasak', 'nasi', 'kopi', 'laptop')
    if external_tokens:
        return False

    # 5. Jika semua token adalah inquiry/operasional dan terdeteksi intent operasional
    if intents & {"persyaratan", "dokumen", "prosedur", "durasi_masa_berlaku", "biaya", "kelayakan_penelitian", "karya_ciptaan"}:
        return True

    return False


# =====================================================
# SEARCH KNOWLEDGE
# =====================================================

def search_knowledge(
    query: str,
    min_score: int = 15,
    history: list[dict[str, str]] | None = None
) -> dict | None:

    data = load_knowledge()
    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    query_tokens = meaningful_tokens(query_normalized)
    detected_topics = detect_topics(query_normalized)
    detected_intents = detect_intents(query_normalized)
    primary_history_topic = get_primary_history_topic(history)

    # -------------------------------------------------
    # GUARD QUERY AMBIGU TANPA TOPIK AKTIF
    # -------------------------------------------------
    if is_ambiguous_query(query_normalized) and not primary_history_topic and not detected_topics:
        return None

    # -------------------------------------------------
    # TOPIK AKTIF (CURRENT OVERRIDES HISTORY)
    # -------------------------------------------------
    active_topic = None
    is_topic_switched = False

    if detected_topics:
        # Utamakan topik HKI jika terdeteksi
        hki_candidates = [t for t in ["paten", "pvt", "merek", "hak_cipta"] if t in detected_topics]
        if hki_candidates:
            active_topic = hki_candidates[0]
        else:
            specific_candidates = [t for t in detected_topics if t != "profil"]
            if specific_candidates:
                active_topic = sorted(specific_candidates)[0]
            else:
                active_topic = sorted(detected_topics)[0]

        if primary_history_topic and active_topic != primary_history_topic:
            is_topic_switched = True
    elif is_follow_up_query(query_normalized):
        # Follow-up: warisi topik terbaru
        active_topic = primary_history_topic
    else:
        # Subjek baru atau bukan follow-up: jangan warisi topik
        active_topic = None

    # Jika tidak ada topik aktif (baik dari query maupun dari riwayat percakapan),
    # pertanyaan yang bergantung pada topik (seperti syarat, alur, dokumen)
    # tidak boleh menebak salah satu topik (seperti paten) secara sepihak.
    if not active_topic:
        if detected_intents:
            return None
        if not query_tokens:
            return None

    results = []

    for item in data.get("knowledge", []):

        item_id = str(item.get("id", "")).lower()
        category = normalize_text(item.get("category", ""))
        searchable_text = build_searchable_text(item)
        searchable_tokens = meaningful_tokens(searchable_text)

        score = 0

        # Tentukan topic dari item (dari id atau category)
        item_topic = None
        for t in list(DOMAIN_KEYWORDS.keys()) + ["paten", "pvt", "merek", "hak_cipta"]:
            if item_id.startswith(t + "_") or item_id == t or category == t:
                item_topic = t
                break

        # -------------------------------------------------
        # 1. TOPIK MATCHING & OVERRIDE
        # -------------------------------------------------
        if detected_topics and item_topic:
            if item_topic in detected_topics:
                score += 80
            else:
                score -= 100
        elif active_topic and item_topic:
            if item_topic == active_topic:
                score += 80
            else:
                score -= 100

        # -------------------------------------------------
        # 2. INTENT MATCHING (SUBTOPIC TARGETING)
        # -------------------------------------------------
        if detected_intents:
            # Persyaratan / Dokumen
            if ("persyaratan" in detected_intents or "dokumen" in detected_intents):
                if "_persyaratan" in item_id:
                    score += 50
                elif "_dokumen" in item_id:
                    score += 45
                elif "_umum" in item_id:
                    score -= 20

            # Prosedur / Alur
            if "prosedur" in detected_intents:
                if "_prosedur" in item_id or "_alur" in item_id:
                    score += 55
                elif "_umum" in item_id:
                    score -= 20

            # Definisi / Pengertian umum
            if "definisi" in detected_intents:
                if "_umum" in item_id or item_id in ["paten", "pvt", "merek", "hak_cipta"]:
                    score += 50

            # Kelayakan hasil penelitian
            if "kelayakan_penelitian" in detected_intents:
                if "_hasil_penelitian" in item_id:
                    score += 70

            # Alasan penolakan merek
            if "penolakan" in detected_intents:
                if "_penolakan" in item_id:
                    score += 70

            # Karya ciptaan
            if "karya_ciptaan" in detected_intents:
                if "_karya" in item_id:
                    score += 70

            # Durasi / Masa Berlaku / Lama Proses
            if "durasi_masa_berlaku" in detected_intents:
                if any(w in query_normalized for w in ["proses", "pengurusan", "mengurus"]):
                    if "_lama_proses" in item_id:
                        score += 70
                    elif "_masa_berlaku" in item_id:
                        score -= 20
                else:
                    if "_masa_berlaku" in item_id:
                        score += 70
                    elif "_lama_proses" in item_id:
                        score -= 20
                if "_umum" in item_id:
                    score -= 30

        # -------------------------------------------------
        # 3. QUESTION OVERLAP SCORE
        # -------------------------------------------------
        questions = item.get("questions", [])
        best_q_score = 0

        if isinstance(questions, list):
            for q in questions:
                q_score = score_question(query_normalized, str(q), query_tokens)
                if q_score > best_q_score:
                    best_q_score = q_score

        score += best_q_score

        # -------------------------------------------------
        # 4. SEARCHABLE TOKEN OVERLAP
        # -------------------------------------------------
        token_matches = query_tokens & searchable_tokens
        score += len(token_matches) * 4

        if score >= min_score:
            results.append({
                "item": item,
                "score": score,
                "item_id": item_id,
            })

    if not results:
        return None

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[0]["item"]


# =====================================================
# GET CLEAN KB ANSWER
# =====================================================

def get_clean_kb_answer(
    item: dict | None,
    query: str = "",
) -> str:
    """
    Menghasilkan jawaban KB yang bersih tanpa metadata internal
    (Kategori, Topik, Informasi yang tersedia, Contoh pertanyaan yang berkaitan).
    Menyertakan dokumen/persyaratan pelengkap jika intent berkaitan.
    """
    if not item or not isinstance(item, dict):
        return ""

    answer = str(item.get("answer", "")).strip()
    item_id = str(item.get("id", "")).lower()

    detected_intents = detect_intents(query)
    if "persyaratan" in detected_intents or "dokumen" in detected_intents:
        all_data = load_knowledge().get("knowledge", [])
        if "_persyaratan" in item_id:
            doc_id = item_id.replace("_persyaratan", "_dokumen")
            doc_item = next((k for k in all_data if k.get("id") == doc_id), None)
            if doc_item and doc_item.get("answer"):
                doc_ans = str(doc_item.get("answer")).strip()
                if doc_ans and doc_ans not in answer:
                    answer = f"{answer}\n\nDokumen yang perlu dipersiapkan:\n{doc_ans}"
        elif "_dokumen" in item_id:
            req_id = item_id.replace("_dokumen", "_persyaratan")
            req_item = next((k for k in all_data if k.get("id") == req_id), None)
            if req_item and req_item.get("answer"):
                req_ans = str(req_item.get("answer")).strip()
                if req_ans and req_ans not in answer:
                    answer = f"Persyaratan permohonan:\n{req_ans}\n\nKelengkapan dokumen:\n{answer}"

    return answer


# =====================================================
# SEARCH KNOWLEDGE FACT (FACT-LEVEL RETRIEVAL)
# =====================================================

def search_knowledge_fact(
    query: str,
    history: list[dict[str, str]] | None = None
) -> dict:
    """
    Mencari fakta di Knowledge Base dan memisahkan antara Topic Found vs Fact Found.

    Returns:
        dict: {
            "item": dict | None,
            "fact_found": bool,
            "score": int,
            "answer": str,
            "topic": str | None,
            "intent": set[str],
        }
    """
    data = load_knowledge()
    query_normalized = normalize_text(query)

    default_result = {
        "item": None,
        "fact_found": False,
        "score": 0,
        "answer": "",
        "topic": None,
        "intent": set(),
    }

    if not query_normalized:
        return default_result

    query_tokens = meaningful_tokens(query_normalized)
    detected_topics = detect_topics(query_normalized)
    detected_intents = detect_intents(query_normalized)
    primary_history_topic = get_primary_history_topic(history)

    # Guard query tanpa domain anchor dan tanpa riwayat in-domain yang valid
    if not has_core_domain_anchor(query_normalized) and not (primary_history_topic and is_follow_up_query(query_normalized)):
        return default_result

    # Guard ambigu tanpa topik
    if is_ambiguous_query(query_normalized) and not primary_history_topic and not detected_topics:
        return default_result

    active_topic = None
    if detected_topics:
        hki_candidates = [t for t in ["paten", "pvt", "merek", "hak_cipta"] if t in detected_topics]
        if hki_candidates:
            active_topic = hki_candidates[0]
        else:
            specific_candidates = [t for t in detected_topics if t != "profil"]
            if specific_candidates:
                active_topic = sorted(specific_candidates)[0]
            else:
                active_topic = sorted(detected_topics)[0]
    elif is_follow_up_query(query_normalized):
        active_topic = primary_history_topic
    else:
        active_topic = None

    if not active_topic:
        if detected_intents or not query_tokens:
            return default_result

    # Jika query memiliki intent biaya, karena KB belum memiliki data biaya resmi,
    # jangan pernah memaksakan item non-biaya (misal paten_umum) sebagai jawaban fakta.
    if "biaya" in detected_intents:
        return {
            "item": None,
            "fact_found": False,
            "score": 0,
            "answer": "",
            "topic": active_topic,
            "intent": detected_intents,
        }

    results = []
    for item in data.get("knowledge", []):
        item_id = str(item.get("id", "")).lower()
        category = normalize_text(item.get("category", ""))
        searchable_text = build_searchable_text(item)
        searchable_tokens = meaningful_tokens(searchable_text)

        score = 0
        item_topic = None
        for t in list(DOMAIN_KEYWORDS.keys()) + ["paten", "pvt", "merek", "hak_cipta"]:
            if item_id.startswith(t + "_") or item_id == t or category == t:
                item_topic = t
                break

        # 1. Topik matching & override
        if detected_topics and item_topic:
            if item_topic in detected_topics:
                score += 80
            else:
                score -= 100
        elif active_topic and item_topic:
            if item_topic == active_topic:
                score += 80
            else:
                score -= 100

        # 2. Intent matching
        if detected_intents:
            if "persyaratan" in detected_intents or "dokumen" in detected_intents:
                if "_persyaratan" in item_id:
                    score += 50
                elif "_dokumen" in item_id:
                    score += 45
                elif "_umum" in item_id:
                    score -= 20

            if "prosedur" in detected_intents:
                if "_prosedur" in item_id or "_alur" in item_id:
                    score += 55
                elif "_umum" in item_id:
                    score -= 20

            if "definisi" in detected_intents:
                if "_umum" in item_id or item_id in ["paten", "pvt", "merek", "hak_cipta", "profil", "lisensi", "tugas", "fungsi"]:
                    score += 50

            if "kelayakan_penelitian" in detected_intents:
                if "_hasil_penelitian" in item_id or "_hasil_pemuliaan" in item_id:
                    score += 70

            if "penolakan" in detected_intents:
                if "_penolakan" in item_id:
                    score += 70

            if "karya_ciptaan" in detected_intents:
                if "_karya" in item_id:
                    score += 70

            if "durasi_masa_berlaku" in detected_intents:
                if any(w in query_normalized for w in ["proses", "pengurusan", "mengurus"]):
                    if "_lama_proses" in item_id:
                        score += 70
                    elif "_masa_berlaku" in item_id:
                        score -= 20
                else:
                    if "_masa_berlaku" in item_id:
                        score += 70
                    elif "_lama_proses" in item_id:
                        score -= 20
                if "_umum" in item_id:
                    score -= 30

        # 3. Question overlap score
        questions = item.get("questions", [])
        best_q_score = 0
        if isinstance(questions, list):
            for q in questions:
                q_score = score_question(query_normalized, str(q), query_tokens)
                if q_score > best_q_score:
                    best_q_score = q_score

        score += best_q_score

        # 4. Searchable token overlap
        token_matches = query_tokens & searchable_tokens
        score += len(token_matches) * 4

        if score >= 15:
            results.append({
                "item": item,
                "score": score,
                "best_q_score": best_q_score,
                "item_id": item_id,
                "item_topic": item_topic,
                "token_matches": token_matches,
            })

    if not results:
        return default_result

    results.sort(key=lambda r: r["score"], reverse=True)
    best = results[0]
    best_item = best["item"]
    best_score = best["score"]
    best_q_score = best["best_q_score"]
    best_id = best["item_id"]
    best_topic = best["item_topic"]

    # Evaluasi FACT_FOUND secara ketat
    fact_found = False

    # A. High confidence question match
    if best_q_score >= 50:
        if (active_topic and best_topic == active_topic) or (detected_topics and best_topic in detected_topics):
            fact_found = True
        elif not active_topic and best_q_score >= 80:
            fact_found = True

    # B. Intent match dengan subtopic yang tepat DAN ada active_topic yang valid
    elif detected_intents and (best_topic == active_topic or (detected_topics and best_topic in detected_topics)):
        if ("persyaratan" in detected_intents or "dokumen" in detected_intents) and ("_persyaratan" in best_id or "_dokumen" in best_id):
            fact_found = True
        elif "prosedur" in detected_intents and ("_prosedur" in best_id or "_alur" in best_id or "_mekanisme" in best_id or "_cara_menggunakan" in best_id):
            fact_found = True
        elif "definisi" in detected_intents and ("_umum" in best_id or best_id in ["paten", "pvt", "merek", "hak_cipta", "profil", "lisensi", "tugas", "fungsi", "pengelolaan_hasil", "pemanfaatan_hasil"]):
            # Untuk definisi, wajibkan topik terdeteksi secara eksplisit pada pesan saat ini
            if detected_topics and (best_topic in detected_topics or best_id in detected_topics or best_id in ["pengelolaan_hasil", "pemanfaatan_hasil"]):
                fact_found = True
        elif "kelayakan_penelitian" in detected_intents and ("_hasil_penelitian" in best_id or "_hasil_pemuliaan" in best_id):
            fact_found = True
        elif "penolakan" in detected_intents and "_penolakan" in best_id:
            fact_found = True
        elif "karya_ciptaan" in detected_intents and "_karya" in best_id:
            fact_found = True
        elif "durasi_masa_berlaku" in detected_intents and ("_masa_berlaku" in best_id or "_lama_proses" in best_id):
            fact_found = True

    # C. Standalone domain item (profil, tugas, fungsi, layanan, petani, lisensi, dll)
    elif (detected_topics or active_topic) and (best_topic in detected_topics or best_topic == active_topic or best_id in DOMAIN_KEYWORDS):
        if best_q_score >= 50:
            fact_found = True

    clean_answer = ""
    if fact_found:
        clean_answer = get_clean_kb_answer(best_item, query_normalized)

    return {
        "item": best_item if fact_found else None,
        "fact_found": fact_found,
        "score": best_score,
        "answer": clean_answer,
        "topic": active_topic,
        "intent": detected_intents,
    }


# =====================================================
# GET KNOWLEDGE CONTEXT
# =====================================================

def get_knowledge_context(
    query: str,
    history: list[dict[str, str]] | None = None
) -> str:

    result = search_knowledge(
        query=query,
        history=history
    )

    if not result:
        return ""

    category = result.get("category", "")
    item_id = result.get("id", "")
    questions = result.get("questions", [])
    answer = result.get("answer", "")

    # Cek apakah ini intent persyaratan/dokumen, dan jika ya, sertakan informasi dokumen pelengkap
    detected_intents = detect_intents(query)
    complementary_text = ""

    if ("persyaratan" in detected_intents or "dokumen" in detected_intents):
        all_data = load_knowledge().get("knowledge", [])
        if "_persyaratan" in item_id:
            doc_id = item_id.replace("_persyaratan", "_dokumen")
            doc_item = next((k for k in all_data if k.get("id") == doc_id), None)
            if doc_item and doc_item.get("answer"):
                complementary_text = f"\n\nDokumen pendukung:\n{doc_item.get('answer')}"
        elif "_dokumen" in item_id:
            req_id = item_id.replace("_dokumen", "_persyaratan")
            req_item = next((k for k in all_data if k.get("id") == req_id), None)
            if req_item and req_item.get("answer"):
                complementary_text = f"\n\nPersyaratan permohonan:\n{req_item.get('answer')}"

    context_parts = [
        f"Kategori: {category} (Topik: {item_id})",
        "Informasi yang tersedia:",
        str(answer) + complementary_text,
    ]

    return "\n".join(context_parts)


# =====================================================
# CORE DOMAIN ANCHORS & DOMAIN GUARD
# =====================================================

CORE_DOMAIN_ANCHORS = {
    # HKI
    "paten",
    "invensi",
    "inventor",
    "dipatenkan",
    "mematenkan",
    "pvt",
    "perlindungan varietas tanaman",
    "perlindungan varietas",
    "varietas tanaman",
    "pemuliaan tanaman",
    "pemulia tanaman",
    "pemulia",
    "merek",
    "merk",
    "merek dagang",
    "merk dagang",
    "merek jasa",
    "merk jasa",
    "hak cipta",
    "karya cipta",
    "pencipta",
    "ciptaan",
    "hki",
    "kekayaan intelektual",
    "djki",

    # Lisensi & Alih Teknologi
    "lisensi",
    "alih teknologi",
    "perjanjian lisensi",
    "royalti",

    # BRMP & Pertanian
    "brmp",
    "brmp pengelola hasil",
    "pengelola hasil",
    "pertanian",
    "petani",
    "usahatani",
    "hasil pertanian",
    "agrikultur",
    "agribisnis",
    "pascapanen",
    "pasca panen",
    "tanaman",
    "panen",
    "sni",

    # Layanan & Operasional BRMP
    "pengaduan",
    "keluhan",
    "aduan",
    "lapor",
    "mengadu",
    "kerja sama",
    "kerjasama",
    "kemitraan",
    "mitra",
    "lokasi",
    "alamat",
    "kantor",
    "kontak",
    "hubungi",
    "menghubungi",
    "menghubunginya",
    "telepon",
    "whatsapp",
    "wa",
    "email",
}

EXTERNAL_POLITICAL_TERMS = {
    "menteri",
    "wakil menteri",
    "presiden",
    "wakil presiden",
    "gubernur",
    "bupati",
    "walikota",
    "dpr",
    "mpr",
    "dpd",
    "partai",
    "pemilu",
    "pilpres",
    "pilkada",
    "kabinet",
}

INSTITUTIONAL_BRMP_ANCHORS = {
    "brmp",
    "brmp pengelola hasil",
    "pengelola hasil",
    "balai",
    "kepala balai",
}


def is_external_political_query(query: str) -> bool:
    """
    Mengecek apakah query merupakan pertanyaan politik / pejabat pemerintahan eksternal
    yang tidak berkaitan dengan entitas kelembagaan BRMP Pengelola Hasil.
    """
    normalized = normalize_text(query)
    if not normalized:
        return False

    has_political = False
    for term in EXTERNAL_POLITICAL_TERMS:
        term_norm = normalize_text(term)
        pattern = rf"(?<!\w){re.escape(term_norm)}(?!\w)"
        if re.search(pattern, normalized):
            has_political = True
            break

    if not has_political:
        return False

    # Jika ada penyebutan entitas BRMP secara eksplisit, bukan sekadar politik eksternal
    for inst in INSTITUTIONAL_BRMP_ANCHORS:
        inst_norm = normalize_text(inst)
        pattern = rf"(?<!\w){re.escape(inst_norm)}(?!\w)"
        if re.search(pattern, normalized):
            return False

    return True


def has_core_domain_anchor(query: str) -> bool:
    """
    Mengecek apakah query secara eksplisit mengandung entitas / kata kunci inti
    domain BRMP, Pertanian, atau HKI.
    """
    normalized = normalize_text(query)
    if not normalized:
        return False

    for anchor in CORE_DOMAIN_ANCHORS:
        anchor_norm = normalize_text(anchor)
        pattern = rf"(?<!\w){re.escape(anchor_norm)}(?!\w)"
        if re.search(pattern, normalized):
            return True

    # Periksa bentuk dasar / stem token
    tokens = [stem_token(w) for w in normalized.split()]
    for t in tokens:
        if t in CORE_DOMAIN_ANCHORS:
            return True

    return False


SPECIFIC_DOMAIN_ANCHORS = {
    "brmp", "brmp pengelola hasil", "pengelola hasil", "balai", "kepala balai",
    "pertanian", "petani", "usahatani", "hasil pertanian", "pascapanen", "pasca panen", "sni",
    "paten", "invensi", "inventor",
    "pvt", "varietas", "pemuliaan", "tanaman",
    "merek", "merk", "brand",
    "hak cipta", "karya cipta", "pencipta", "ciptaan", "karya",
    "hki", "kekayaan intelektual", "djki",
    "lisensi", "alih teknologi", "perjanjian lisensi", "royalti",
}


def is_query_in_domain(
    query: str,
    active_topic: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> bool:
    """
    Memvalidasi apakah query berada dalam ruang lingkup domain resmi BRMP/HKI/Pertanian.
    Mencegah query out-of-domain lolos ke Groq API.
    """
    normalized = normalize_text(query)
    if not normalized:
        return False

    # 1. Pertanyaan kepemimpinan politik / kabinet umum tanpa entitas institusi BRMP adalah OOD
    if is_external_political_query(normalized):
        return False

    # 2. Cek apakah ada token eksternal di luar domain dan inquiry tokens
    words = meaningful_tokens(normalized)
    external_tokens = {
        w for w in words
        if w not in INQUIRY_AND_OPERATIONAL_TOKENS
        and stem_token(w) not in INQUIRY_AND_OPERATIONAL_TOKENS
        and w not in CORE_DOMAIN_ANCHORS
    }
    if external_tokens:
        # Jika membawa token eksternal (misal 'tukang', 'nasi', 'python', 'bitcoin'),
        # wajib memiliki anchor domain spesifik secara eksplisit
        has_specific = any(
            re.search(rf"(?<!\w){re.escape(a)}(?!\w)", normalized)
            for a in SPECIFIC_DOMAIN_ANCHORS
        )
        if not has_specific:
            return False

    # 3. Jika query memiliki core domain anchor secara eksplisit
    if has_core_domain_anchor(normalized):
        return True

    # 4. Jika query merupakan genuine follow-up pada sesi dengan topik riwayat yang valid
    primary_history = get_primary_history_topic(history)
    if primary_history and is_follow_up_query(normalized):
        return True

    return False


# =====================================================
# GET ALL KNOWLEDGE
# =====================================================

def get_all_knowledge():

    data = load_knowledge()
    return data.get("knowledge", [])


# =====================================================
# SUGGESTED QUESTIONS RESOLVER (CONTEXT-AWARE & DETERMINISTIC)
# =====================================================

STARTER_SUGGESTED_QUESTIONS = [
    "Apa itu paten?",
    "Apa itu PVT?",
    "Apa saja layanan BRMP Pengelola Hasil?",
]

TOPIC_SUGGESTED_QUESTIONS = {
    "pvt": [
        "Apa saja persyaratan PVT?",
        "Bagaimana alur pengajuan PVT?",
        "Dokumen apa yang dibutuhkan untuk PVT?",
        "Berapa lama masa perlindungan PVT?",
    ],
    "paten": [
        "Apa saja persyaratan paten?",
        "Bagaimana alur pendaftaran paten?",
        "Dokumen apa yang dibutuhkan untuk paten?",
        "Berapa lama masa perlindungan paten?",
    ],
    "merek": [
        "Apa saja syarat pendaftaran merek?",
        "Bagaimana alur pendaftaran merek?",
        "Dokumen apa saja untuk pendaftaran merek?",
        "Berapa lama masa berlaku merek?",
    ],
    "hak_cipta": [
        "Apa saja syarat pencatatan hak cipta?",
        "Bagaimana alur pencatatan hak cipta?",
        "Karya apa saja yang dapat dilindungi hak cipta?",
        "Berapa lama masa perlindungan hak cipta?",
    ],
    "layanan": [
        "Layanan apa saja untuk petani?",
        "Bagaimana cara konsultasi ke BRMP?",
        "Apa saja program pelatihan BRMP?",
    ],
    "petani": [
        "Layanan apa saja untuk petani?",
        "Bagaimana cara konsultasi ke BRMP?",
        "Apa saja program pelatihan BRMP?",
    ],
    "lisensi": [
        "Bagaimana mekanisme lisensi teknologi BRMP?",
        "Apa saja hasil teknologi yang dapat dilisensikan?",
        "Bagaimana cara mengajukan kerja sama lisensi?",
    ],
    "konsultasi": [
        "Bagaimana cara konsultasi ke BRMP?",
        "Layanan apa saja untuk petani?",
        "Bagaimana cara menghubungi BRMP?",
    ],
    "kontak": [
        "Di mana alamat kantor BRMP Pengelola Hasil?",
        "Bagaimana cara menghubungi BRMP?",
        "Apa website resmi BRMP Pengelola Hasil?",
    ],
    "lokasi": [
        "Di mana alamat kantor BRMP Pengelola Hasil?",
        "Bagaimana cara menghubungi BRMP?",
        "Apa website resmi BRMP Pengelola Hasil?",
    ],
    "website": [
        "Apa website resmi BRMP Pengelola Hasil?",
        "Bagaimana cara menghubungi BRMP?",
        "Di mana alamat kantor BRMP Pengelola Hasil?",
    ],
    "pengaduan": [
        "Bagaimana cara menyampaikan pengaduan ke BRMP?",
        "Bagaimana cara menghubungi BRMP?",
        "Di mana alamat kantor BRMP Pengelola Hasil?",
    ],
    "kerjasama": [
        "Bagaimana cara mengajukan kerja sama dengan BRMP?",
        "Apa saja bentuk kerja sama dengan BRMP?",
        "Bagaimana cara menghubungi BRMP?",
    ],
    "pelatihan": [
        "Apa saja program pelatihan BRMP?",
        "Layanan apa saja untuk petani?",
        "Bagaimana cara konsultasi ke BRMP?",
    ],
    "program": [
        "Apa saja program pelatihan BRMP?",
        "Layanan apa saja untuk petani?",
        "Teknologi apa yang digunakan BRMP Pengelola Hasil?",
    ],
    "teknologi": [
        "Teknologi apa yang digunakan BRMP Pengelola Hasil?",
        "Layanan apa saja untuk petani?",
        "Bagaimana BRMP membantu pasar hasil pertanian?",
    ],
    "pasar": [
        "Bagaimana BRMP membantu pasar hasil pertanian?",
        "Layanan apa saja untuk petani?",
        "Teknologi apa yang digunakan BRMP Pengelola Hasil?",
    ],
    "profil": [
        "Apa tugas utama BRMP Pengelola Hasil?",
        "Apa saja layanan BRMP Pengelola Hasil?",
        "Bagaimana cara menghubungi BRMP?",
    ],
    "tugas": [
        "Apa saja fungsi BRMP Pengelola Hasil?",
        "Apa saja layanan BRMP Pengelola Hasil?",
        "Bagaimana cara menghubungi BRMP?",
    ],
    "fungsi": [
        "Apa tugas utama BRMP Pengelola Hasil?",
        "Apa saja layanan BRMP Pengelola Hasil?",
        "Bagaimana cara menghubungi BRMP?",
    ],
}


def normalize_suggestion_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def resolve_suggested_questions(
    topic: str | None = None,
    current_query: str | None = None,
    history: list[dict[str, str]] | None = None,
    max_suggestions: int = 3,
) -> list[str]:
    """
    Menentukan daftar suggested questions yang relevan berdasarkan topik percakapan
    secara deterministic, bebas halusinasi, dan melakukan deduplikasi terhadap
    pertanyaan pengguna terbaru maupun riwayat percakapan.
    """
    if not topic or topic not in TOPIC_SUGGESTED_QUESTIONS:
        return list(STARTER_SUGGESTED_QUESTIONS[:max_suggestions])

    candidate_questions = TOPIC_SUGGESTED_QUESTIONS.get(topic, [])

    # Kumpulkan pertanyaan yang sudah ditanyakan oleh user untuk deduplikasi
    asked_normalized = set()
    if current_query:
        asked_normalized.add(normalize_suggestion_text(current_query))

    if history:
        for item in history:
            if isinstance(item, dict) and item.get("role") == "user":
                content = item.get("content", "")
                if content:
                    asked_normalized.add(normalize_suggestion_text(content))

    filtered_suggestions = []
    seen = set()

    for q in candidate_questions:
        q_norm = normalize_suggestion_text(q)
        if not q_norm or q_norm in seen:
            continue

        # Cek apakah persis sama atau mirip dengan pertanyaan yang baru/sudah ditanyakan
        is_duplicate = False
        for asked in asked_normalized:
            if q_norm == asked or (len(asked) > 6 and (q_norm in asked or asked in q_norm)):
                is_duplicate = True
                break

        if not is_duplicate:
            filtered_suggestions.append(q)
            seen.add(q_norm)

        if len(filtered_suggestions) >= max_suggestions:
            break

    # Jika setelah filtering tersisa kurang dari 1, ambil kandidat tanpa filtering ketat terhadap history lama
    if not filtered_suggestions and candidate_questions:
        curr_norm = normalize_suggestion_text(current_query or "")
        for q in candidate_questions:
            q_norm = normalize_suggestion_text(q)
            if q_norm != curr_norm and q_norm not in seen:
                filtered_suggestions.append(q)
                seen.add(q_norm)
            if len(filtered_suggestions) >= max_suggestions:
                break

    return filtered_suggestions[:max_suggestions]