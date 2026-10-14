from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.chatbot import router as chatbot_router


app = FastAPI(
    title="BRMP Pengelola Hasil Chatbot"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================
# ROUTES
# ==========================================

app.include_router(
    chatbot_router
)


@app.get("/")
def root():

    return {
        "message":
        "BRMP Chatbot API aktif"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }