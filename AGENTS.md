# ATURAN AGEN — BACKEND

## 1. Teknologi

Backend menggunakan:

* Python
* FastAPI
* Pydantic
* Groq API
* JSON data/configuration

---

## 2. Struktur Backend

Struktur utama:

```text
backend/
├── main.py
├── routes/
├── schemas/
├── services/
└── data/
```

Tanggung jawab:

### main.py

Entry point aplikasi dan registrasi router.

### routes/

Menangani HTTP request dan response.

Route harus tetap tipis.

### schemas/

Menangani validasi request dan response menggunakan schema.

### services/

Berisi business logic.

### data/

Berisi konfigurasi dan data chatbot.

---

## 3. Aturan Service

Pisahkan tanggung jawab:

```text
chat_service.py
    → orkestrasi percakapan

flow_service.py
    → navigasi predefined flow

knowledge_service.py
    → pencarian knowledge

groq_service.py
    → komunikasi dengan AI provider
```

Jangan memindahkan seluruh logic ke satu file.

Jangan membuat service baru jika service yang sudah ada masih
dapat digunakan.

## 4. Route

Route tidak boleh berisi business logic yang kompleks.

Gunakan:

```text
Route
  ↓
Service
  ↓
Data / AI
```

Hindari:

```text
Route
  ↓
Semua business logic
  ↓
AI
  ↓
Database/Data
```

## 5. Perubahan Schema

Jika mengubah schema:

1. Cari seluruh penggunaannya.
2. Periksa route.
3. Periksa service.
4. Periksa frontend.
5. Jalankan testing.

## 6. Session

Pertahankan konsistensi:

```text
session_id
conversation history
current state
chat mode
```

Jangan mengubah mekanisme session tanpa audit.

## 7. Groq / AI

API key harus berasal dari environment variable.

Jangan hardcode:

```python
GROQ_API_KEY = "..."
```

Gunakan konfigurasi environment.

Jangan menampilkan detail internal provider AI kepada pengguna
chatbot.

## 8. Error Handling

Jangan menyembunyikan error.

Hindari:

```python
try:
    ...
except Exception:
    pass
```

Error harus ditangani dengan jelas.

## 9. Testing Backend

Setelah perubahan backend, gunakan test yang relevan.

Minimal pertimbangkan:

```bash
python -m compileall .
```

Jika project memiliki pytest:

```bash
python -m pytest
```

Jika mengubah API:

* jalankan backend
* test endpoint
* periksa request
* periksa response
* periksa error response

## 10. JSON

Setelah mengubah:

```text
data/chatbot_flow.json
data/knowledge_base.json
```

wajib:

* validasi JSON
* periksa field
* periksa ID
* periksa referensi
* test chatbot

## 11. Larangan

Jangan:

* rewrite service tanpa alasan
* membuat duplicate service
* mengubah API tanpa memeriksa frontend
* menghapus session logic tanpa analisis
* mengubah data JSON secara massal tanpa validasi
* menghapus error handling yang sudah ada
* menambahkan dependency tanpa alasan
