import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException

from schemas.chat import ChatRequest
from services.chat_service import (
    process_chat,
    process_start,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["Chatbot"],
)


# =====================================================
# START CHAT
# =====================================================

@router.post("/start")
def start_chat(
    request: ChatRequest | None = None,
):
    """
    Membuat atau melanjutkan session chatbot.
    """
    session_id = None
    mode = "flow"

    if request:
        session_id = request.session_id
        mode = request.mode

    try:
        return process_start(
            session_id=session_id,
            mode=mode,
        )
    except Exception as error:
        logger.error(f"Error in start_chat: {error}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Layanan chatbot sedang mengalami kendala saat memulai sesi. Silakan coba lagi.",
        )


# =====================================================
# CHAT
# =====================================================

@router.post("")
def chat(
    request: ChatRequest,
):
    """
    Memproses pesan chatbot berdasarkan mode.
    """
    try:
        return process_chat(
            message=request.message,
            current_node_id=request.current_node_id,
            option_id=request.option_id,
            session_id=request.session_id,
            mode=request.mode,
        )
    except Exception as error:
        logger.error(f"Error in chat endpoint: {error}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Layanan chatbot sedang mengalami kendala saat memproses pesan Anda. Silakan coba lagi.",
        )