import logging
import re
import uuid

from services.flow_service import (
    get_node,
    get_initial_node,
    find_option,
)

from services.knowledge_service import (
    get_knowledge_context,
    search_knowledge_fact,
    is_ambiguous_query,
    detect_topics,
    detect_intents,
    is_query_in_domain,
    is_external_political_query,
    has_core_domain_anchor,
    resolve_suggested_questions,
    get_primary_history_topic,
    STARTER_SUGGESTED_QUESTIONS,
)

from services.groq_service import (
    generate_response,
)

logger = logging.getLogger(__name__)


# =====================================================
# CONVERSATION MEMORY
# =====================================================

MAX_HISTORY = 10

conversation_sessions: dict[
    str,
    list[dict[str, str]]
] = {}


# =====================================================
# CHAT MODE
# =====================================================

FLOW_MODE = "flow"
CHAT_MODE = "chat"


# =====================================================
# START CHAT
# =====================================================

def process_start(
    session_id: str | None = None,
    mode: str = FLOW_MODE,
):
    """
    Memulai atau melanjutkan percakapan.

    Pergantian Flow <-> Chat tidak menghapus memory.
    """

    mode = normalize_mode(mode)

    if not session_id:
        session_id = str(uuid.uuid4())

    ensure_session(session_id)

    # -------------------------------------------------
    # CHAT START
    # -------------------------------------------------

    if mode == CHAT_MODE:

        return {
            "id": "chat_start",
            "type": "ai",
            "message": (
                "Halo! 👋 Saya asisten informasi BRMP Pengelola Hasil. "
                "Senang bisa membantu Anda. Ada yang ingin Anda tanyakan "
                "seputar layanan, HKI, informasi BRMP, atau hal lain "
                "yang berkaitan dengan layanan kami?"
            ),
            "options": [],
            "actions": [],
            "suggested_questions": list(STARTER_SUGGESTED_QUESTIONS),
            "session_id": session_id,
            "mode": CHAT_MODE,
        }

    # -------------------------------------------------
    # FLOW START
    # -------------------------------------------------

    node = get_initial_node()

    return attach_session_id(
        node,
        session_id,
        FLOW_MODE,
    )


# =====================================================
# NORMALIZATION
# =====================================================

def normalize_text(text: str | None) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def normalize_mode(mode: str | None) -> str:

    if normalize_text(mode) == CHAT_MODE:
        return CHAT_MODE

    return FLOW_MODE


# =====================================================
# SESSION HELPERS
# =====================================================

def ensure_session(
    session_id: str,
):
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = []


def get_session_history(
    session_id: str | None,
) -> list[dict[str, str]]:

    if not session_id:
        return []

    ensure_session(session_id)

    return conversation_sessions[session_id]


def add_history(
    session_id: str,
    role: str,
    content: str,
):
    if not content:
        return

    ensure_session(session_id)

    conversation_sessions[session_id].append(
        {
            "role": role,
            "content": content,
        }
    )

    if len(conversation_sessions[session_id]) > MAX_HISTORY:

        conversation_sessions[session_id] = (
            conversation_sessions[session_id][-MAX_HISTORY:]
        )


def attach_session_id(
    node: dict | None,
    session_id: str,
    mode: str,
):

    if not node:
        return None

    result = dict(node)

    result["session_id"] = session_id
    result["mode"] = mode

    return result


# =====================================================
# FLOW MEMORY
# =====================================================

def save_flow_conversation(
    session_id: str,
    user_message: str,
    assistant_message: str,
):
    """
    Menyimpan percakapan Flow agar tetap tersedia
    ketika user berpindah ke Chat Mode.
    """

    if user_message:
        add_history(
            session_id,
            "user",
            user_message,
        )

    if assistant_message:
        add_history(
            session_id,
            "assistant",
            assistant_message,
        )


# =====================================================
# TEXT HELPERS
# =====================================================

def contains_any(
    text: str,
    keywords: list[str],
) -> bool:

    normalized = normalize_text(text)

    return any(
        keyword in normalized
        for keyword in keywords
    )


def is_greeting(
    text: str,
) -> bool:

    normalized = normalize_text(text)

    greetings = [
        "hai",
        "halo",
        "hello",
        "hi",
        "pagi",
        "selamat pagi",
        "siang",
        "selamat siang",
        "sore",
        "selamat sore",
        "malam",
        "selamat malam",
        "permisi",
    ]

    if normalized in greetings:
        return True

    return any(
        normalized.startswith(
            greeting + " "
        )
        for greeting in greetings
    )


def is_thanks(
    text: str,
) -> bool:

    return contains_any(
        text,
        [
            "terima kasih",
            "makasih",
            "thanks",
            "thank you",
            "trimakasih",
            "trims",
            "tks",
        ],
    )


def is_farewell(
    text: str,
) -> bool:

    return contains_any(
        text,
        [
            "dadah",
            "sampai jumpa",
            "sampai ketemu",
            "bye",
            "goodbye",
            "selamat tinggal",
        ],
    )


def is_small_talk(
    text: str,
) -> bool:

    return contains_any(
        text,
        [
            "apa kabar",
            "kabarmu",
            "kamu siapa",
            "siapa kamu",
            "kamu suka makan apa",
            "suka makan apa",
            "kamu bisa apa",
            "bisa bantu saya",
            "bisa membantu saya",
            "bisa bantu",
            "kamu membantu apa",
        ],
    )


# =====================================================
# NATURAL RESPONSE
# =====================================================

def get_natural_response(
    text: str,
) -> str | None:

    normalized = normalize_text(text)

    if is_greeting(normalized):

        return (
            "Halo! 👋 Saya asisten informasi BRMP Pengelola Hasil. "
            "Senang bisa membantu Anda. Ada yang ingin Anda tanyakan "
            "seputar layanan, HKI, informasi BRMP, atau hal lain yang "
            "berkaitan dengan layanan kami?"
        )

    if is_thanks(normalized):

        return (
            "Sama-sama! 😊 Senang bisa membantu. "
            "Kalau masih ada yang ingin ditanyakan, silakan."
        )

    if is_farewell(normalized):

        return (
            "Sampai jumpa! 👋 Semoga informasinya bermanfaat. "
            "Silakan kembali lagi kalau membutuhkan bantuan."
        )

    if is_small_talk(normalized):

        if (
            "kamu suka makan" in normalized
            or "suka makan apa" in normalized
        ):
            return (
                "Hehe, saya sendiri tidak makan 😄 "
                "Tapi kalau ada yang ingin Anda tanyakan tentang "
                "BRMP Pengelola Hasil atau layanan HKI, saya dengan "
                "senang hati membantu."
            )

        if (
            "kamu siapa" in normalized
            or "siapa kamu" in normalized
        ):
            return (
                "Saya asisten informasi BRMP Pengelola Hasil. 😊 "
                "Saya bisa membantu memberikan informasi seputar "
                "BRMP, layanan, serta HKI seperti paten, PVT, "
                "merek, dan hak cipta."
            )

        return (
            "Tentu 😊 Saya siap membantu. Anda bisa menanyakan "
            "informasi tentang BRMP Pengelola Hasil, layanan, "
            "HKI seperti paten, PVT, merek, atau hak cipta. "
            "Kalau belum tahu harus mulai dari mana, ceritakan "
            "saja kebutuhan Anda."
        )

    return None


# =====================================================
# FLOW KEYWORDS
#
# PENTING:
# ID DI SINI HARUS SESUAI DENGAN chatbot_flow.json
# =====================================================

FLOW_KEYWORDS = {

    # -------------------------------------------------
    # PATEN
    # -------------------------------------------------

    "paten_persyaratan": [
        "syarat paten",
        "persyaratan paten",
        "syarat mengajukan paten",
        "persyaratan mengajukan paten",
        "ketentuan pengajuan paten",
        "syarat pendaftaran paten",
        "dokumen paten",
        "dokumen yang diperlukan untuk paten",
        "dokumen untuk mengajukan paten",
        "kelengkapan dokumen paten",
        "berkas pengajuan paten",
        "apa yang harus disiapkan untuk paten",
    ],

    "paten_alur": [
        "cara mengajukan paten",
        "bagaimana cara mengajukan paten",
        "mau mengajukan paten",
        "cara daftar paten",
        "prosedur paten",
        "prosedur pengajuan paten",
        "prosedur pendaftaran paten",
        "ingin mendaftarkan paten",
        "pengajuan hak paten",
        "bagaimana mengurus paten",
        "tahapan pengajuan paten",
        "tahapan pendaftaran paten",
        "langkah mengajukan paten",
        "bagaimana langkah pengajuan paten",
        "mau paten",
        "pengen paten",
        "alur paten",
    ],

    "paten": [
        "apa itu paten",
        "informasi mengenai paten",
        "jelaskan tentang paten",
        "saya ingin tahu tentang paten",
        "paten itu apa",
        "pengertian paten",
        "hak paten itu apa",
        "apa yang dimaksud dengan paten",
        "tentang paten",
        "informasi paten",
    ],

    # -------------------------------------------------
    # PVT
    # -------------------------------------------------

    "pvt_persyaratan": [
        "syarat pvt",
        "persyaratan pvt",
        "apa saja syarat pvt",
        "syarat perlindungan varietas tanaman",
        "ketentuan pvt",
        "syarat mengajukan pvt",
        "persyaratan mengajukan pvt",
        "dokumen pvt",
        "dokumen yang diperlukan untuk pvt",
        "dokumen untuk mengajukan pvt",
        "apa saja dokumen pvt",
        "berkas pvt",
        "kelengkapan dokumen pvt",
        "dokumen perlindungan varietas tanaman",
        "apa yang harus disiapkan untuk pvt",
    ],

    "pvt_alur": [
        "cara mengajukan pvt",
        "bagaimana cara mengajukan pvt",
        "cara daftar pvt",
        "prosedur pvt",
        "prosedur pendaftaran pvt",
        "tahapan pvt",
        "tahapan pendaftaran pvt",
        "langkah mengajukan pvt",
        "bagaimana mengurus pvt",
        "ingin mendaftarkan varietas tanaman",
        "alur pvt",
    ],

    "hak_pvt": [
        "apa itu pvt",
        "apa itu perlindungan varietas tanaman",
        "jelaskan pvt",
        "informasi mengenai pvt",
        "pvt itu apa",
        "hak pvt itu apa",
        "perlindungan varietas tanaman itu apa",
        "apa yang dimaksud perlindungan varietas tanaman",
        "tentang pvt",
        "informasi pvt",
    ],

    # -------------------------------------------------
    # MEREK
    # -------------------------------------------------

    "merek_persyaratan": [
        "syarat merek",
        "persyaratan pendaftaran merek",
        "apa saja syarat merek",
        "syarat daftar merek",
        "ketentuan pendaftaran merek",
        "persyaratan mengajukan merek",
        "dokumen merek",
        "dokumen yang diperlukan untuk merek",
        "dokumen pendaftaran merek",
        "apa saja dokumen merek",
        "berkas pendaftaran merek",
        "kelengkapan dokumen merek",
        "apa yang harus disiapkan untuk daftar merek",
        "dokumen pengajuan merek",
    ],

    "merek_alur": [
        "cara daftar merek",
        "bagaimana cara mendaftarkan merek",
        "cara mengajukan merek",
        "prosedur pendaftaran merek",
        "tahapan pendaftaran merek",
        "langkah daftar merek",
        "bagaimana mengurus merek",
        "ingin mendaftarkan merek",
        "cara mendaftarkan merek dagang",
        "cara daftar merek usaha",
        "alur merek",
    ],

    "merek": [
        "apa itu merek",
        "apa itu merek dagang",
        "apa itu merek jasa",
        "jelaskan merek",
        "informasi mengenai merek",
        "merek itu apa",
        "fungsi merek",
        "kenapa merek perlu didaftarkan",
        "tentang merek",
        "informasi merek",
    ],

    # -------------------------------------------------
    # HAK CIPTA
    # -------------------------------------------------

    "hak_cipta_persyaratan": [
        "syarat hak cipta",
        "persyaratan hak cipta",
        "apa saja syarat hak cipta",
        "syarat pencatatan hak cipta",
        "persyaratan pencatatan ciptaan",
        "ketentuan hak cipta",
        "syarat mendaftarkan hak cipta",
        "dokumen hak cipta",
        "dokumen pencatatan hak cipta",
        "dokumen yang diperlukan untuk hak cipta",
        "apa saja dokumen hak cipta",
        "berkas pencatatan hak cipta",
        "kelengkapan dokumen hak cipta",
        "apa yang harus disiapkan untuk hak cipta",
        "dokumen pengajuan hak cipta",
    ],

    "hak_cipta_alur": [
        "cara daftar hak cipta",
        "cara mengajukan hak cipta",
        "bagaimana cara mendaftarkan hak cipta",
        "prosedur pencatatan hak cipta",
        "tahapan hak cipta",
        "tahapan pencatatan hak cipta",
        "langkah mencatatkan hak cipta",
        "bagaimana mengurus hak cipta",
        "ingin mendaftarkan hak cipta",
        "cara mencatatkan karya",
        "alur hak cipta",
    ],

    "hak_cipta": [
        "apa itu hak cipta",
        "jelaskan hak cipta",
        "informasi mengenai hak cipta",
        "hak cipta itu apa",
        "apa yang dimaksud hak cipta",
        "fungsi hak cipta",
        "tentang hak cipta",
        "informasi hak cipta",
    ],

    # -------------------------------------------------
    # BRMP / LAYANAN
    # -------------------------------------------------

    "layanan_1": [
        "layanan petani",
        "layanan teknis",
        "informasi untuk petani",
    ],

    "informasi_perakitan_modernisasi": [
        "perakitan dan modernisasi",
        "informasi perakitan",
        "modernisasi pertanian",
    ],

    "informasi_sni": [
        "sni",
        "standar nasional indonesia",
    ],

    "layanan_3": [
        "pemanfaatan",
        "pemanfaatan hasil pertanian",
    ],

    "pemanfaatan_persyaratan": [
        "syarat pemanfaatan",
        "persyaratan pemanfaatan",
    ],

    "pemanfaatan_alur": [
        "alur pemanfaatan",
        "prosedur pemanfaatan",
        "cara pemanfaatan",
    ],

    "jam_layanan": [
        "jam layanan",
        "jam kerja",
        "jam buka",
        "buka jam berapa",
    ],

    "layanan_4": [
        "layanan konsultasi",
        "konsultasi",
    ],

    "konsultasi_persyaratan": [
        "syarat konsultasi",
        "persyaratan konsultasi",
    ],

    "konsultasi_alur": [
        "alur konsultasi",
        "prosedur konsultasi",
        "cara konsultasi",
    ],
}


# =====================================================
# FLOW TARGET FROM CURRENT NODE
# =====================================================

def find_target_from_options(
    node: dict | None,
    message: str,
):

    if not node:
        return None

    normalized = normalize_text(message)

    items = (
        node.get("options", [])
        + node.get("actions", [])
    )

    for item in items:

        label = normalize_text(
            item.get("label")
            or item.get("title")
            or item.get("text")
            or ""
        )

        if not label:
            continue

        if normalized == label:

            return (
                item.get("next_node_id")
                or item.get("node_id")
                or item.get("target")
            )

    return None


# =====================================================
# FLOW TARGET FROM MESSAGE
# =====================================================

def find_flow_from_message(
    message: str,
):

    normalized = normalize_text(message)

    # -------------------------------------------------
    # SPESIFIK -> UMUM
    # -------------------------------------------------

    priority = [
        "paten_persyaratan",
        "paten_alur",

        "pvt_persyaratan",
        "pvt_alur",

        "merek_persyaratan",
        "merek_alur",

        "hak_cipta_persyaratan",
        "hak_cipta_alur",
    ]

    for node_id in priority:

        keywords = FLOW_KEYWORDS.get(
            node_id,
            [],
        )

        if any(
            keyword in normalized
            for keyword in keywords
        ):
            return node_id

    # -------------------------------------------------
    # NODE UMUM HKI
    # -------------------------------------------------

    general_order = [
        "paten",
        "hak_pvt",
        "merek",
        "hak_cipta",
    ]

    for node_id in general_order:

        keywords = FLOW_KEYWORDS.get(
            node_id,
            [],
        )

        if any(
            keyword in normalized
            for keyword in keywords
        ):
            return node_id

    # -------------------------------------------------
    # LAYANAN
    # -------------------------------------------------

    for node_id, keywords in FLOW_KEYWORDS.items():

        if node_id in priority:
            continue

        if node_id in general_order:
            continue

        if any(
            keyword in normalized
            for keyword in keywords
        ):
            return node_id

    return None


# =====================================================
# FOLLOW-UP
# =====================================================

FOLLOW_UP_KEYWORDS = [
    "syarat",
    "persyaratan",
    "dokumen",
    "berkas",
    "caranya",
    "cara",
    "prosedur",
    "proses",
    "tahapan",
    "langkah",
    "selanjutnya",
    "lanjut",
    "terus",
    "berapa lama",
    "jangka waktu",
]


def is_follow_up_question(
    message: str,
) -> bool:

    normalized = normalize_text(message)

    if not normalized:
        return False

    return any(
        keyword in normalized
        for keyword in FOLLOW_UP_KEYWORDS
    )


# =====================================================
# RECENT TOPIC
# =====================================================

def get_recent_topic(
    history: list[dict[str, str]],
) -> str | None:
    return get_primary_history_topic(history)


# =====================================================
# FOLLOW-UP -> ACTUAL FLOW NODE
# =====================================================

def get_topic_node_from_follow_up(
    message: str,
    topic: str | None,
):

    if not topic:
        return None

    normalized = normalize_text(message)

    if not is_follow_up_question(normalized):
        return None

    # -------------------------------------------------
    # PATEN
    # -------------------------------------------------

    if topic == "paten":

        if (
            "cara" in normalized
            or "prosedur" in normalized
            or "proses" in normalized
            or "tahapan" in normalized
            or "langkah" in normalized
            or "alur" in normalized
        ):
            return "paten_alur"

        return "paten_persyaratan"

    # -------------------------------------------------
    # PVT
    # -------------------------------------------------

    if topic == "pvt":

        if (
            "cara" in normalized
            or "prosedur" in normalized
            or "proses" in normalized
            or "tahapan" in normalized
            or "langkah" in normalized
            or "alur" in normalized
        ):
            return "pvt_alur"

        return "pvt_persyaratan"

    # -------------------------------------------------
    # MEREK
    # -------------------------------------------------

    if topic == "merek":

        if (
            "cara" in normalized
            or "prosedur" in normalized
            or "proses" in normalized
            or "tahapan" in normalized
            or "langkah" in normalized
            or "alur" in normalized
        ):
            return "merek_alur"

        return "merek_persyaratan"

    # -------------------------------------------------
    # HAK CIPTA
    # -------------------------------------------------

    if topic == "hak_cipta":

        if (
            "cara" in normalized
            or "prosedur" in normalized
            or "proses" in normalized
            or "tahapan" in normalized
            or "langkah" in normalized
            or "alur" in normalized
        ):
            return "hak_cipta_alur"

        return "hak_cipta_persyaratan"

    return None


# =====================================================
# BUILD FLOW RESPONSE
# =====================================================

def get_flow_node_response(
    node_id: str,
    session_id: str,
    user_message: str,
    message_override: str | None = None,
):

    node = get_node(node_id)

    if not node:
        return None

    assistant_message = (
        message_override
        if message_override is not None
        else (
            node.get("message")
            or node.get("text")
            or ""
        )
    )

    save_flow_conversation(
        session_id,
        user_message,
        assistant_message,
    )

    return attach_session_id(
        node,
        session_id,
        FLOW_MODE,
    ) | {
        "message": assistant_message,
    }


# =====================================================
# FLOW QUESTION ANSWER + CONTINUE FLOW
# =====================================================

def answer_flow_question(
    message: str,
    session_id: str,
    target_node_id: str,
):

    """
    Menjawab pertanyaan user menggunakan knowledge base,
    kemudian tetap melanjutkan Flow berdasarkan target node.

    Contoh:

    User:
        Apa itu paten?

    AI:
        Paten merupakan ...

        Kalau Anda ingin mengetahui lebih lanjut,
        silakan pilih informasi yang ingin Anda ketahui.

    Options:
        Persyaratan
        Bagaimana Alurnya?
        Kembali ke Paten
    """

    target_node = get_node(
        target_node_id
    )

    if not target_node:
        return None

    history = get_session_history(
        session_id
    )

    context = get_knowledge_context(
        query=message,
        history=history,
    )

    if not context:
        return None

    # Simpan pertanyaan user
    add_history(
        session_id,
        "user",
        message,
    )

    history = get_session_history(
        session_id
    )

    response = generate_response(
        message=message,
        context=context,
        history=history,
        mode=FLOW_MODE,
    )

    if not response:
        return None

    continuation = (
        "Kalau Anda ingin mengetahui lebih lanjut, "
        "silakan pilih informasi yang ingin Anda ketahui."
    )

    final_message = (
        f"{response.strip()}\n\n"
        f"{continuation}"
    )

    add_history(
        session_id,
        "assistant",
        final_message,
    )

    result = dict(target_node)

    result["message"] = final_message
    result["session_id"] = session_id
    result["mode"] = FLOW_MODE

    return result


# =====================================================
# DIRECT CHAT
# =====================================================

def process_direct_chat(
    message: str,
    session_id: str,
):

    ensure_session(session_id)

    normalized = normalize_text(
        message
    )

    # -------------------------------------------------
    # NATURAL RESPONSE
    # -------------------------------------------------

    natural_response = get_natural_response(
        normalized
    )

    if natural_response:

        add_history(
            session_id,
            "user",
            message,
        )

        add_history(
            session_id,
            "assistant",
            natural_response,
        )

        suggested_q = (
            list(STARTER_SUGGESTED_QUESTIONS)
            if is_greeting(normalized)
            else []
        )

        return {
            "id": "natural_response",
            "type": "ai",
            "message": natural_response,
            "options": [],
            "actions": [],
            "suggested_questions": suggested_q,
            "session_id": session_id,
            "mode": CHAT_MODE,
        }

    # -------------------------------------------------
    # PRIOR HISTORY
    # -------------------------------------------------

    prior_history = list(
        get_session_history(
            session_id
        )
    )

    detected = detect_topics(message)
    recent_topic = get_recent_topic(prior_history)

    # -------------------------------------------------
    # AMBIGUOUS QUERY WITHOUT TOPIC
    # -------------------------------------------------

    if is_ambiguous_query(message) and not recent_topic and not detected:

        clarification = (
            "Maksudnya ingin mengetahui bagaimana tentang apa ya? 😊 "
            "Anda bisa menanyakan informasi seputar paten, PVT, merek, "
            "hak cipta, atau layanan BRMP Pengelola Hasil."
        )

        add_history(
            session_id,
            "user",
            message,
        )

        add_history(
            session_id,
            "assistant",
            clarification,
        )

        return {
            "id": "clarification_response",
            "type": "ai",
            "message": clarification,
            "options": [],
            "actions": [],
            "suggested_questions": list(STARTER_SUGGESTED_QUESTIONS),
            "session_id": session_id,
            "mode": CHAT_MODE,
        }

    # -------------------------------------------------
    # KNOWLEDGE FACT RETRIEVAL (KB-FIRST)
    # -------------------------------------------------

    knowledge_result = search_knowledge_fact(
        query=message,
        history=prior_history,
    )

    if knowledge_result and knowledge_result.get("fact_found"):
        response = knowledge_result.get("answer")
        matched_item = knowledge_result.get("item")
        matched_id = matched_item.get("id") if isinstance(matched_item, dict) else None
        logger.info(
            f"KB-First Direct Answer: matched_item={matched_id}, "
            f"score={knowledge_result.get('score')}, topic={knowledge_result.get('topic')}, "
            f"response_source=knowledge_base, groq_called=False"
        )
    else:
        active_topic = knowledge_result.get("topic") if knowledge_result else None
        in_domain = is_query_in_domain(
            query=message,
            active_topic=active_topic,
            history=prior_history,
        )

        if not in_domain:
            logger.info(
                f"Domain Guard Intercepted: query='{message}', topic={active_topic}, "
                f"response_source=domain_fallback, groq_called=False"
            )
            response = (
                "Maaf, saya hanya bisa membantu pertanyaan yang berkaitan dengan "
                "BRMP Pengelola Hasil, layanan, pengelolaan hasil pertanian, atau HKI. "
                "Silakan tanyakan hal yang ingin Anda ketahui seputar topik tersebut."
            )
        else:
            logger.info(
                f"KB-First Fallback to Groq: query='{message}', topic={active_topic}, "
                f"response_source=groq_fallback, groq_called=True"
            )
            response = generate_response(
                message=message,
                context="",
                history=prior_history,
                mode=CHAT_MODE,
            )

            if not response:
                response = (
                    "Untuk pertanyaan tersebut saya belum memiliki "
                    "informasi yang cukup. Kalau yang Anda cari "
                    "berkaitan dengan BRMP Pengelola Hasil, layanan, "
                    "atau HKI, silakan jelaskan sedikit lebih spesifik."
                )

    # -------------------------------------------------
    # SUGGESTED QUESTIONS RESOLUTION (CONTEXT-AWARE)
    # -------------------------------------------------

    active_topic = knowledge_result.get("topic") if knowledge_result else None
    intents = detect_intents(message)
    is_external_definition = ("definisi" in intents and not detected and not is_ambiguous_query(message))
    is_political = is_external_political_query(message)

    if is_political or (is_external_definition and not has_core_domain_anchor(message)):
        # True OOD / non-domain definition: Reset to safe starter suggestions without topic leakage
        effective_topic = None
    elif detected:
        # 1. Topic explicitly mentioned in current query (e.g. topic switch to merek)
        hki_candidates = [t for t in ["paten", "pvt", "merek", "hak_cipta"] if t in detected]
        effective_topic = hki_candidates[0] if hki_candidates else sorted(detected)[0]
    elif active_topic:
        # 2. Active topic from knowledge retrieval
        effective_topic = active_topic
    elif recent_topic:
        # 3. Inherited recent topic from conversation session
        effective_topic = recent_topic
    else:
        effective_topic = None

    suggested_questions = resolve_suggested_questions(
        topic=effective_topic,
        current_query=message,
        history=prior_history,
    )

    # -------------------------------------------------
    # SAVE CONVERSATION
    # -------------------------------------------------

    add_history(
        session_id,
        "user",
        message,
    )

    add_history(
        session_id,
        "assistant",
        response,
    )

    return {
        "id": "ai_response",
        "type": "ai",
        "message": response,
        "options": [],
        "actions": [],
        "suggested_questions": suggested_questions,
        "session_id": session_id,
        "mode": CHAT_MODE,
    }


# =====================================================
# MAIN PROCESS
# =====================================================

def process_chat(
    message: str | None = None,
    current_node_id: str | None = None,
    option_id: str | None = None,
    session_id: str | None = None,
    mode: str = FLOW_MODE,
):

    mode = normalize_mode(
        mode
    )

    # -------------------------------------------------
    # SESSION
    # -------------------------------------------------

    if not session_id:
        session_id = str(uuid.uuid4())

    ensure_session(
        session_id
    )

    message = message or ""

    normalized_message = normalize_text(
        message
    )

    # =================================================
    # CHAT MODE
    # =================================================

    if mode == CHAT_MODE:

        if not normalized_message:

            return process_start(
                session_id=session_id,
                mode=CHAT_MODE,
            )

        return process_direct_chat(
            message=message,
            session_id=session_id,
        )

    # =================================================
    # FLOW MODE
    # =================================================

    # -------------------------------------------------
    # 1. OPTION CLICK
    #
    # WAJIB PALING ATAS.
    #
    # Button click tidak boleh masuk ke AI.
    # -------------------------------------------------

    if current_node_id and option_id:

        current_node = get_node(
            current_node_id
        )

        if current_node:

            selected_option = find_option(
                current_node,
                option_id,
            )

            if selected_option:

                target_node_id = (
                    selected_option.get("next_node_id")
                    or selected_option.get("node_id")
                    or selected_option.get("target")
                )

                if target_node_id:

                    node = get_node(
                        target_node_id
                    )

                    if node:

                        label = (
                            selected_option.get("label")
                            or selected_option.get("title")
                            or selected_option.get("text")
                            or message
                        )

                        assistant_message = (
                            node.get("message")
                            or node.get("text")
                            or ""
                        )

                        save_flow_conversation(
                            session_id,
                            label,
                            assistant_message,
                        )

                        return attach_session_id(
                            node,
                            session_id,
                            FLOW_MODE,
                        )

    # -------------------------------------------------
    # 2. EMPTY INPUT
    # -------------------------------------------------

    if not normalized_message:

        if current_node_id:

            node = get_node(
                current_node_id
            )

            if node:

                return attach_session_id(
                    node,
                    session_id,
                    FLOW_MODE,
                )

        return attach_session_id(
            get_initial_node(),
            session_id,
            FLOW_MODE,
        )

    # -------------------------------------------------
    # 3. HOME
    # -------------------------------------------------

    home_keywords = [
        "menu utama",
        "menu awal",
        "kembali ke menu",
        "kembali ke utama",
        "beranda",
    ]

    if normalized_message in home_keywords:

        node = get_initial_node()

        save_flow_conversation(
            session_id,
            message,
            node.get("message", ""),
        )

        return attach_session_id(
            node,
            session_id,
            FLOW_MODE,
        )

    # -------------------------------------------------
    # 4. TEXT YANG SAMA DENGAN OPTION NODE SAAT INI
    # -------------------------------------------------

    current_node = None

    if current_node_id:

        current_node = get_node(
            current_node_id
        )

    if current_node:

        target_node_id = find_target_from_options(
            current_node,
            normalized_message,
        )

        if target_node_id:

            node = get_node(
                target_node_id
            )

            if node:

                save_flow_conversation(
                    session_id,
                    message,
                    node.get("message", ""),
                )

                return attach_session_id(
                    node,
                    session_id,
                    FLOW_MODE,
                )

    # -------------------------------------------------
    # 5. NATURAL RESPONSE
    #
    # Greeting/thanks hanya ditangani jika tidak
    # merupakan navigasi Flow.
    # -------------------------------------------------

    natural_response = get_natural_response(
        normalized_message
    )

    if natural_response:

        save_flow_conversation(
            session_id,
            message,
            natural_response,
        )

        # Tetap pertahankan node Flow saat ini.
        if current_node:

            result = dict(current_node)

            result["message"] = natural_response
            result["session_id"] = session_id
            result["mode"] = FLOW_MODE

            return result

        return {
            "id": "flow_natural_response",
            "type": "ai",
            "message": natural_response,
            "options": [],
            "actions": [
                {
                    "id": "main_menu",
                    "label": "📋 Kembali ke Menu",
                }
            ],
            "session_id": session_id,
            "mode": FLOW_MODE,
        }

    # -------------------------------------------------
    # 6. DETEKSI FOLLOW-UP BERDASARKAN MEMORY
    #
    # Dilakukan sebelum keyword umum.
    # -------------------------------------------------

    history = get_session_history(
        session_id
    )

    recent_topic = get_recent_topic(
        history
    )

    follow_up_node = get_topic_node_from_follow_up(
        normalized_message,
        recent_topic,
    )

    if follow_up_node:

        node = get_node(
            follow_up_node
        )

        if node:

            save_flow_conversation(
                session_id,
                message,
                node.get("message", ""),
            )

            return attach_session_id(
                node,
                session_id,
                FLOW_MODE,
            )

    # -------------------------------------------------
    # 7. FLOW TARGET BERDASARKAN PESAN
    # -------------------------------------------------

    flow_node_id = find_flow_from_message(
        normalized_message
    )

    if flow_node_id:

        # ---------------------------------------------
        # Untuk pertanyaan langsung:
        #
        # "Apa itu paten?"
        #
        # jawab AI dari knowledge lalu tampilkan
        # option dari node Flow.
        # ---------------------------------------------

        if flow_node_id in [
            "paten",
            "hak_pvt",
            "merek",
            "hak_cipta",
        ]:

            ai_result = answer_flow_question(
                message=message,
                session_id=session_id,
                target_node_id=flow_node_id,
            )

            if ai_result:

                return ai_result

        # ---------------------------------------------
        # Pertanyaan spesifik:
        #
        # "Syarat paten?"
        #
        # langsung ke node Flow yang sesuai.
        # ---------------------------------------------

        node = get_node(
            flow_node_id
        )

        if node:

            save_flow_conversation(
                session_id,
                message,
                node.get("message", ""),
            )

            return attach_session_id(
                node,
                session_id,
                FLOW_MODE,
            )

    # -------------------------------------------------
    # 8. KNOWLEDGE + AI DI FLOW
    #
    # Jika pertanyaan berkaitan dengan BRMP tetapi
    # tidak memiliki node Flow yang cocok.
    #
    # Setelah AI menjawab, tetap tampilkan option
    # dari node saat ini.
    # -------------------------------------------------

    history = get_session_history(
        session_id
    )

    context = get_knowledge_context(
        query=message,
        history=history,
    )

    if context:

        add_history(
            session_id,
            "user",
            message,
        )

        response = generate_response(
            message=message,
            context=context,
            history=get_session_history(session_id),
            mode=FLOW_MODE,
        )

        if response:

            continuation = (
                "Kalau Anda ingin mengetahui lebih lanjut, "
                "silakan pilih informasi yang tersedia "
                "pada panduan ini."
            )

            final_message = (
                f"{response.strip()}\n\n"
                f"{continuation}"
            )

            add_history(
                session_id,
                "assistant",
                final_message,
            )

            if current_node:

                result = dict(current_node)

                result["message"] = final_message
                result["session_id"] = session_id
                result["mode"] = FLOW_MODE

                return result

            return {
                "id": "flow_ai_response",
                "type": "ai",
                "message": final_message,
                "options": [],
                "actions": [
                    {
                        "id": "main_menu",
                        "label": "📋 Menu Utama",
                    }
                ],
                "session_id": session_id,
                "mode": FLOW_MODE,
            }

    # -------------------------------------------------
    # 9. FALLBACK
    # -------------------------------------------------

    fallback = (
        "Sepertinya saya belum menangkap maksudnya 😊 "
        "Saya lebih fokus membantu informasi seputar "
        "BRMP Pengelola Hasil, layanan, dan HKI. "
        "Silakan pilih informasi yang ingin Anda cari "
        "melalui panduan yang tersedia."
    )

    save_flow_conversation(
        session_id,
        message,
        fallback,
    )

    if current_node:

        result = dict(current_node)

        result["message"] = fallback
        result["session_id"] = session_id
        result["mode"] = FLOW_MODE

        return result

    return {
        "id": "flow_fallback",
        "type": "ai",
        "message": fallback,
        "options": [],
        "actions": [
            {
                "id": "main_menu",
                "label": "📋 Menu Utama",
            }
        ],
        "session_id": session_id,
        "mode": FLOW_MODE,
    }


# =====================================================
# DEBUG
# =====================================================

def debug_get_session_history(
    session_id: str,
):
    return conversation_sessions.get(
        session_id,
        [],
    )

