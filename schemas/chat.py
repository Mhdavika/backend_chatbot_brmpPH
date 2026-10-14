from typing import Literal, Optional

# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class ChatRequest(BaseModel):

    message: str | None = None

    current_node_id: str | None = None

    option_id: str | None = None

    session_id: str | None = None

    mode: Literal[
        "flow",
        "chat",
    ] = "flow"


class ChatResponse(BaseModel):

    id: str

    type: str

    message: str

    title: Optional[str] = None

    image: Optional[str] = None

    options: list = []

    actions: list = []

    open_url: Optional[str] = None

    session_id: Optional[str] = None

    suggested_questions: list[str] = []

    mode: Literal[
        "flow",
        "chat",
    ] = "flow"