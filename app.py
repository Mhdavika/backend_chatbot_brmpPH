import os
import uvicorn
import gradio as gr

from main import app as fastapi_app


# ==========================================
# Gradio dummy interface
# ==========================================

def chatbot():
    return "BRMP Pengelola Hasil Chatbot API aktif"


demo = gr.Interface(
    fn=chatbot,
    inputs=[],
    outputs="text",
    title="BRMP Pengelola Hasil Chatbot",
    description="Backend API untuk Chatbot BRMP Pengelola Hasil",
)


# ==========================================
# Mount Gradio ke FastAPI
# ==========================================

app = gr.mount_gradio_app(
    fastapi_app,
    demo,
    path="/",
)


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
    )