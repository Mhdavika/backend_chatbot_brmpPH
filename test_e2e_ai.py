import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()

from services.chat_service import process_chat, conversation_sessions

def run_e2e_tests():
    conversation_sessions.clear()
    
    print("=" * 60)
    print("RUNNING END-TO-END SIMULATED CHAT TESTS")
    print("=" * 60)

    # -------------------------------------------------------------
    # 1. TOPIC SWITCHING & FOLLOW UP IN ONE MULTI-TURN SESSION
    # -------------------------------------------------------------
    sess = "sess_e2e_switching"
    turns = [
        "Apa itu paten?",
        "Apa saja persyaratannya?",
        "Kalau PVT bagaimana?",
        "Syaratnya apa?",
        "Kalau merek?",
        "Dokumen yang diperlukan apa?",
        "Hak cipta itu apa?",
        "Alurnya bagaimana?",
    ]

    print("\n--- MULTI-TURN SESSION: Topic Switching & Follow-ups ---")
    for msg in turns:
        res = process_chat(message=msg, session_id=sess, mode="chat")
        print(f"\nUser: {msg}")
        print(f"Bot : {res.get('message')}")

    # -------------------------------------------------------------
    # 2. CONDITIONAL FACTS
    # -------------------------------------------------------------
    sess_cond = "sess_e2e_cond"
    print("\n--- TEST: Conditional Facts ---")
    res_cond = process_chat(message="Saya dengar syarat paten cukup KTP saja, benar?", session_id=sess_cond, mode="chat")
    print("\nUser: Saya dengar syarat paten cukup KTP saja, benar?")
    print(f"Bot : {res_cond.get('message')}")

    # -------------------------------------------------------------
    # 3. OUT-OF-DOMAIN & UNAVAILABLE INFO
    # -------------------------------------------------------------
    sess_ood = "sess_e2e_ood"
    print("\n--- TEST: Out of Domain & Unavailable Info ---")
    
    res_pres = process_chat(message="Siapa presiden Indonesia sekarang?", session_id=sess_ood, mode="chat")
    print("\nUser: Siapa presiden Indonesia sekarang?")
    print(f"Bot : {res_pres.get('message')}")

    res_biaya = process_chat(message="Berapa biaya membuat paten?", session_id=sess_ood, mode="chat")
    print("\nUser: Berapa biaya membuat paten?")
    print(f"Bot : {res_biaya.get('message')}")

    # -------------------------------------------------------------
    # 4. AMBIGUOUS QUERIES
    # -------------------------------------------------------------
    sess_fresh = "sess_fresh_amb"
    print("\n--- TEST: Ambiguous Query in Fresh Session ---")
    res_amb = process_chat(message="gimana?", session_id=sess_fresh, mode="chat")
    print("\nUser: gimana?")
    print(f"Bot : {res_amb.get('message')}")

if __name__ == "__main__":
    run_e2e_tests()
