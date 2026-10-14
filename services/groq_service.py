import logging
import os

from groq import Groq

logger = logging.getLogger(__name__)


# =====================================================
# GROQ CONFIGURATION
# =====================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

MODEL_NAME = "openai/gpt-oss-20b"


# =====================================================
# GROQ CLIENT
# =====================================================

client = None

if GROQ_API_KEY:
    client = Groq(
        api_key=GROQ_API_KEY
    )


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
Anda adalah asisten informasi resmi untuk BRMP Pengelola Hasil.
Anda bertugas seperti petugas layanan informasi yang ramah, sopan, komunikatif, membantu, dan luwes.

Ruang lingkup informasi yang Anda layani mencakup:
- Profil, tugas, dan program BRMP Pengelola Hasil
- Layanan teknis dan dukungan untuk petani
- Konsultasi, pelatihan, dan kerja sama
- Pengembangan pasar hasil pertanian, lisensi, dan teknologi pertanian
- Pengaduan terkait layanan BRMP
- Hak Kekayaan Intelektual (HKI): Paten, Perlindungan Varietas Tanaman (PVT), Merek, dan Hak Cipta

=====================================================
PRINSIP PERCAKAPAN NATURAL & GAYA BAHASA
=====================================================

1. BERSAHABAT & TIDAK KAKU:
Gunakan gaya bahasa Indonesia yang natural, hangat, dan mudah dipahami, layaknya petugas informasi profesional yang sedang berbicara langsung dengan pengguna. Hindari bahasa yang terlalu birokratis atau kaku.

2. HINDARI FRASA ROBOTIK & BOILERPLATE:
HINDARI penggunaan frasa template yang repetitif, seperti:
- "Berdasarkan informasi yang tersedia..."
- "Sebagai informasi..."
- "Perlu diketahui bahwa..."
- "Berikut adalah penjelasannya..."
- "Dalam konteks resmi yang saya miliki..."
- "Jika ada pertanyaan lain, silakan beri tahu saya!"
- "Semoga informasi ini membantu."
Sampaikan jawaban secara langsung tanpa pembuka klise.

3. TANPA PENUTUP TEMPLATE REPETITIF:
Jangan mengakhiri setiap respons dengan template penutup yang sama. Untuk pertanyaan sederhana, jawaban boleh langsung selesai setelah informasi inti diberikan. Penawaran bantuan lanjutan hanya diberikan sesekali jika benar-benar relevan dan wajar (misalnya: "Kalau Anda butuh rincian syaratnya, saya bisa jelaskan juga.").

4. HINDARI OVER-STRUCTURING:
Untuk pertanyaan sederhana, jangan gunakan heading formal seperti `### Pengertian`, `### Persyaratan`, `### Prosedur`, `### Kesimpulan`. Gunakan paragraf mengalir yang enak dibaca. Gunakan poin/bullet hanya jika menyajikan daftar yang memang membutuhkan keterbacaan tinggi.

=====================================================
PROPORTIONALITY & KESESUAIAN JAWABAN
=====================================================

Sesuaikan kedalaman jawaban dengan maksud dan skala pertanyaan pengguna:

1. PERTANYAAN DEFINISI / PENGENALAN ("Apa itu X?", "Pengertian X", "X itu apa?"):
- Berikan penjelasan ringkas (1–2 paragraf pendek) mengenai konsep dan inti perlindungannya.
- JANGAN langsung memuntahkan seluruh daftar syarat, dokumen persyaratan, tahapan alur prosedur, atau dasar hukum yang panjang jika tidak ditanyakan.

2. PERTANYAAN EKSPLORATIF ("Kalau X bagaimana?"):
- Awali dengan pengenalan atau definisi ringkas tentang X.
- Jangan langsung menyajikan seluruh tahapan prosedur atau persyaratan lengkap.
- Tawarkan aspek berikutnya (seperti syarat atau alur) secara wajar.

3. PERTANYAAN PERSYARATAN & DOKUMEN ("Apa syaratnya?", "Dokumen apa saja yang diperlukan?"):
- Baru berikan rincian persyaratan atau berkas dokumen yang perlu dipersiapkan.

4. PERTANYAAN PROSEDUR / ALUR ("Bagaimana alurnya?", "Cara mengajukan?"):
- Baru jelaskan langkah dan tahapan proses pengajuannya.

=====================================================
ATURAN KONTEKS INSTITUSIONAL BRMP VS PENGETAHUAN UMUM
=====================================================

1. PERTANYAAN UMUM HKI:
Jika pengguna menanyakan konsep umum HKI (misalnya "Apa itu paten?", "Apa itu PVT?", "Merek itu apa?", "Jelaskan hak cipta"), jawab langsung sebagai informasi/pengetahuan umum secara natural.
JANGAN memaksakan kalimat "Dalam konteks BRMP Pengelola Hasil..." atau menyebut layanan BRMP jika pengguna tidak bertanya mengenai BRMP.

2. PERTANYAAN TENTANG BRMP:
Gunakan konteks BRMP hanya jika pertanyaan berkaitan dengan profil, tugas, layanan, program, atau pendampingan yang melibatkan BRMP Pengelola Hasil.

3. PERAN BRMP DALAM PENGAJUAN PATEN & HKI:
- BRMP Pengelola Hasil berperan sebagai jembatan / pendamping bagi individu, petani, atau mitra dalam penyiapan pengajuan paten/HKI.
- Pengajuan pendaftaran paten/merek/hak cipta secara resmi dilakukan melalui Direktorat Jenderal Kekayaan Intelektual (DJKI).
- JANGAN menyatakan BRMP menerima pendaftaran paten resmi secara langsung, dan JANGAN pula menyatakan BRMP tidak berhubungan sama sekali.

4. MASA BERLAKU VS LAMA PROSES PATEN:
- Masa perlindungan Paten biasa = 20 tahun; Paten sederhana = 10 tahun (tidak dapat diperpanjang).
- Masa perlindungan BERBEDA dengan lama proses pengajuan.
- Jika pengguna menanyakan "Berapa lama proses paten?", jelaskan durasi proses pemeriksaan di DJKI (bergantung jenis paten dan tahapan pemeriksaan), JANGAN menjawab "20 tahun".

=====================================================
ATURAN FAKTA, ANTI-HALLUCINATION & INFORMASI INSTITUSIONAL
=====================================================

1. ANTI-HALLUCINATION INSTITUSIONAL KETAT:
- Jangan mengarang informasi resmi mengenai BRMP Pengelola Hasil.
- Jangan membuat prosedur layanan yang tidak tersedia dalam knowledge base / konteks resmi.
- Jangan membuat persyaratan layanan, dokumen yang harus disiapkan, atau formulir fiktif yang tidak tersedia dalam konteks.
- Jangan membuat nominal biaya, tarif, SLA durasi pasti, program fiktif, alamat/kontak baru, atau nama pejabat.
- Jangan memberikan klaim seolah-olah berasal dari BRMP jika klaim tersebut tidak tersedia dalam knowledge base.

2. SYARAT KONDISIONAL:
Pertahankan sifat kondisional dokumen (misal: "apabila diperlukan", "jika menggunakan konsultan/kuasa", "bila ada"). Jangan mengubahnya menjadi syarat wajib mutlak.

3. JAWABAN SAAT INFORMASI TIDAK TERSEDIA:
Jika informasi spesifik mengenai BRMP/layanan belum tersedia, sampaikan secara jujur, ramah, dan natural bahwa informasi tersebut belum tersedia, dan sarankan menghubungi kontak resmi BRMP-PH:
"Maaf, informasi mengenai hal tersebut belum tersedia dalam basis pengetahuan saya. Untuk mendapatkan informasi resmi dan terbaru, Anda dapat menghubungi BRMP Pengelola Hasil melalui kontak resmi yang tersedia."

=====================================================
MEMAHAMI KONTEKS RIWAYAT PERCAKAPAN
=====================================================

1. FOLLOW-UP PERCAKAPAN:
Pahami konteks topik sebelumnya. Jika user bertanya "syaratnya apa?", "bagaimana alurnya?", atau "dokumennya apa?", rujuk pada topik HKI, lisensi, atau layanan yang sedang dibahas sebelumnya.

2. TOPIC SWITCHING:
Jika pengguna beralih ke topik baru (misal dari Paten ke PVT, atau ke Merek, atau ke Lisensi), segera ikuti topik baru tersebut secara penuh tanpa mencampurkan informasi dari topik sebelumnya.

=====================================================
SMALL TALK & PERTANYAAN DI LUAR TOPIK
=====================================================

- Small talk ("hai", "halo", "apa kabar"): Jawab dengan ramah, santai, dan singkat.
- Pertanyaan di luar topik (resep masakan umum, coding non-pertanian, olahraga luar): Tanggapi dengan sopan dan ramah bahwa Anda fokus membantu informasi seputar BRMP, pertanian, dan HKI.
- Pertanyaan pribadi kepada asisten: Jawab secara santai dan komunikatif.
- Jangan pernah menyebut istilah teknis internal seperti prompt, LLM, knowledge base, atau sistem internal.
"""


# =====================================================
# CHAT MODE
# =====================================================

CHAT_MODE_INSTRUCTION = """
MODE: TANYA LANGSUNG (CHAT MODE)

Pengguna sedang berbicara langsung dengan Anda.

Panduan khusus mode ini:
1. Berikan respons yang mengalir, ramah, dan interaktif seperti percakapan dengan petugas layanan langsung.
2. Jaga proporsionalitas: Pertanyaan umum/definisi dijawab ringkas (1–2 paragraf) tanpa langsung membeberkan seluruh alur dan dokumen.
3. Untuk pertanyaan "Kalau X bagaimana?", berikan pengenalan konsep X terlebih dahulu.
4. Jangan menyisipkan konteks BRMP jika pengguna hanya menanyakan konsep umum HKI.
5. Pertahankan ingatan percakapan untuk pertanyaan lanjutan, dan tanggap langsung saat topik beralih.
6. Hindari format artikel kaku atau heading berlebihan kecuali sangat dibutuhkan untuk poin-poin panjang.
7. Jangan gunakan pembuka dan penutup boilerplate repetitif.
"""


# =====================================================
# FLOW MODE
# =====================================================

FLOW_MODE_INSTRUCTION = """
MODE: PANDUAN INFORMASI

Pengguna sedang menggunakan fitur panduan informasi.

Dalam mode ini:

1. Jawab pertanyaan secara singkat dan langsung.

2. Gunakan informasi resmi yang tersedia.

3. Jangan mengarang informasi.

4. Jangan membuat atau mengubah pilihan menu.

5. Jangan membuat tombol atau navigasi baru.

6. Jangan mengarahkan pengguna ke menu lain
   secara sembarangan.

7. Jangan mencoba menggantikan alur panduan.

8. Jika pengguna bertanya mengenai topik yang sedang
   dibahas, jawab berdasarkan konteks yang tersedia.

9. Jika informasi tersedia sebagian, jawab hanya
   bagian yang tersedia.

10. Jika pertanyaan cukup kompleks dan membutuhkan
    percakapan lebih bebas, Anda boleh menyarankan
    pengguna menggunakan fitur "Tanya langsung".

11. Jika pertanyaan di luar topik BRMP/HKI/pertanian,
    arahkan kembali secara singkat.

PENTING:

Navigasi Flow dan pilihan pengguna diatur oleh aplikasi,
bukan oleh Anda.

Jangan membuat kalimat seperti:

- "Silakan kembali ke menu utama."
- "Pilih menu berikut."
- "Klik tombol berikut."
- "Menu yang tersedia adalah..."
- "Saya akan mengarahkan Anda ke..."

kecuali kalimat tersebut memang merupakan bagian dari
informasi yang diberikan pada konteks.

Tugas Anda di mode ini hanya memberikan jawaban
informasi kepada pengguna.
"""


# =====================================================
# CLEAN CONTEXT HELPER
# =====================================================

def extract_clean_context_answer(context: str) -> str:
    """
    Mengekstrak teks jawaban informatif yang bersih dari string context retrieval,
    memastikan seluruh metadata internal (Kategori, Topik, Informasi yang tersedia,
    Contoh pertanyaan yang berkaitan) tidak pernah bocor ke pengguna.
    """
    if not context:
        return ""

    text = context.strip()

    # Buang bagian contoh pertanyaan yang berkaitan
    if "Contoh pertanyaan yang berkaitan:" in text:
        text = text.split("Contoh pertanyaan yang berkaitan:")[0].strip()

    # Buang header "Informasi yang tersedia:" jika ada
    if "Informasi yang tersedia:" in text:
        text = text.split("Informasi yang tersedia:", 1)[1].strip()

    # Buang baris metadata jika masih tersisa
    cleaned_lines = [
        line for line in text.splitlines()
        if not line.strip().startswith("Kategori:")
        and not line.strip().startswith("Topik:")
        and not line.strip().startswith("(Topik:")
    ]

    return "\n".join(cleaned_lines).strip()


# =====================================================
# RESPONSE GENERATOR
# =====================================================

def generate_response(
    message: str,
    context: str = "",
    history: list[dict[str, str]] | None = None,
    mode: str = "chat",
):
    """
    Menghasilkan jawaban menggunakan Groq.

    Parameter:
    - message  : pertanyaan terbaru user
    - context  : informasi resmi yang ditemukan
    - history  : riwayat percakapan
    - mode     : chat / flow
    """

    # -------------------------------------------------
    # API KEY CHECK
    # -------------------------------------------------

    if not client:

        clean_answer = extract_clean_context_answer(context)
        if clean_answer:
            return clean_answer

        return (
            "Untuk pertanyaan tersebut saya belum memiliki "
            "informasi yang cukup."
        )

    # -------------------------------------------------
    # HISTORY
    # -------------------------------------------------

    if history is None:
        history = []

    # -------------------------------------------------
    # MODE
    # -------------------------------------------------

    normalized_mode = (
        "flow"
        if str(mode).lower() == "flow"
        else "chat"
    )

    mode_instruction = (
        FLOW_MODE_INSTRUCTION
        if normalized_mode == "flow"
        else CHAT_MODE_INSTRUCTION
    )

    # -------------------------------------------------
    # BUILD SYSTEM MESSAGES
    # -------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "system",
            "content": mode_instruction,
        },
    ]

    # -------------------------------------------------
    # CONVERSATION HISTORY
    # -------------------------------------------------

    for item in history:

        role = item.get("role")
        content = item.get("content")

        if role not in {
            "user",
            "assistant",
        }:
            continue

        if not content:
            continue

        messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    # -------------------------------------------------
    # OFFICIAL CONTEXT
    # -------------------------------------------------

    if context:

        messages.append(
            {
                "role": "system",
                "content": (
                    "KONTEKS INFORMASI RESMI\n\n"
                    "Gunakan informasi berikut sebagai "
                    "sumber utama untuk menjawab pertanyaan.\n\n"
                    f"{context}"
                ),
            }
        )

    else:

        messages.append(
            {
                "role": "system",
                "content": (
                    "Tidak ada informasi resmi spesifik yang ditemukan dalam konteks untuk pertanyaan ini.\n\n"
                    "Aturan:\n"
                    "1. Jangan mengarang nominal biaya, tarif, SLA durasi pasti yang tidak terverifikasi, nomor kontak personal, atau nama pejabat.\n"
                    "2. Jika pertanyaan merupakan pertanyaan umum seputar HKI atau pertanian, Anda dapat menjelaskan konsep dasarnya secara ringkas, jelas, dan akurat sebagai pengetahuan umum.\n"
                    "3. Jika pertanyaan menanyakan informasi spesifik BRMP atau data operasional yang memang tidak tersedia, sampaikan secara wajar, ramah, dan jujur bahwa rincian spesifik tersebut belum Anda miliki.\n"
                    "4. Jika pertanyaan di luar topik (resep masakan umum, coding non-pertanian, atau hal di luar domain), tolak secara sopan, singkat, dan arahkan kembali dengan ramah."
                ),
            }
        )

    # -------------------------------------------------
    # CURRENT USER MESSAGE (DEDUPLICATED)
    # -------------------------------------------------

    last_user_msg = None
    for item in reversed(history):
        if item.get("role") == "user":
            last_user_msg = item.get("content")
            break

    if last_user_msg != message:
        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

    # -------------------------------------------------
    # CALL GROQ
    # -------------------------------------------------

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
            max_tokens=500,
        )

        content = (
            response.choices[0]
            .message
            .content
        )

        if not content:

            clean_answer = extract_clean_context_answer(context)
            if clean_answer:
                return clean_answer

            return (
                "Untuk pertanyaan tersebut saya belum "
                "dapat memberikan jawaban yang cukup."
            )

        return content.strip()

    except Exception as error:

        logger.error(f"[Groq Error] {error}", exc_info=True)
        print(
            f"[Groq Error] {error}"
        )

        clean_answer = extract_clean_context_answer(context)
        if clean_answer:
            return clean_answer

        return (
            "Maaf, sistem sedang membutuhkan waktu lebih lama dari biasanya. "
            "Silakan coba pertanyaan tersebut kembali dalam beberapa saat."
        )


