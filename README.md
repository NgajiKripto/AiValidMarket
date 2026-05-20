# AiValidMarket

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-SDK-412991?style=for-the-badge&logo=openai&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Platform AI Agent untuk Validasi Ide Bisnis & Produk**

*Cek apakah ada market untuk ide kamu, temukan keyword pencarian, pertanyaan yang relevan di internet, dan sumber informasi dari berbagai platform.*

[Mulai Sekarang](#-instalasi) | [Fitur](#-fitur) | [Dokumentasi API](#-api-endpoints) | [Kontribusi](#-kontribusi)

</div>

---

## Daftar Isi

- [Tentang Proyek](#-tentang-proyek)
- [Fitur](#-fitur)
- [Cara Kerja](#-cara-kerja)
- [Tech Stack](#-tech-stack)
- [Arsitektur](#-arsitektur)
- [Prasyarat](#-prasyarat)
- [Instalasi](#-instalasi)
- [Konfigurasi Environment](#-konfigurasi-environment)
- [Menjalankan Aplikasi](#-menjalankan-aplikasi)
- [Docker](#-docker)
- [Testing](#-testing)
- [API Endpoints](#-api-endpoints)
- [Kontribusi](#-kontribusi)
- [Lisensi](#-lisensi)

---

## Tentang Proyek

**AiValidMarket** adalah platform AI agent yang membantu user memvalidasi ide bisnis atau produk mereka. Platform ini secara otomatis:

- Mengecek apakah ada market untuk ide yang diajukan
- Mencari keyword pencarian yang relevan
- Menemukan pertanyaan yang sering ditanyakan orang di internet
- Mengumpulkan sumber informasi dari website, sosial media, dan data geografis

Platform ini terinspirasi oleh arsitektur [MiroFish](https://github.com/666ghj/MiroFish) - multi-agent prediction engine.

---

## Fitur

### 1. Idea Analyzer
AI menganalisis ide bisnis/produk dan menghasilkan:
- Keywords pencarian yang relevan
- Pertanyaan pasar (apa yang orang tanyakan)
- Target audience
- Kategori pasar
- Hint kompetitor

### 2. Web Researcher
Mencari data nyata dari internet via Serper API:
- Hasil pencarian Google
- "People Also Ask" (pertanyaan terkait)
- Berita terbaru
- Social media (Reddit, Twitter/X, LinkedIn)

### 3. Report Generator
AI agent dengan pola **ReACT** (Reasoning + Acting) menghasilkan laporan lengkap:
- Market viability score (1-10)
- Executive summary
- Analisis keyword
- Analisis pertanyaan pasar
- Sumber informasi terkategorisasi
- Rekomendasi aksi

### 4. Interactive Chat
Tanya jawab lanjutan dengan AI tentang hasil validasi. User bisa menggali lebih dalam aspek tertentu dari laporan.

### 5. Async Task Processing
Background thread processing dengan progress polling real-time. User tidak perlu menunggu - bisa melihat progress step by step.

### 6. Brutalist UI
Desain minimalis hitam/putih dengan aksen oranye (#FF4500), font JetBrains Mono. Clean, fokus pada konten.

---

## Cara Kerja

```
1. User mendeskripsikan ide bisnis/produk di halaman utama
         |
         v
2. AI Agent menganalisis ide --> keywords, pertanyaan pasar, kategori
         |
         v
3. Web Researcher mencari data nyata di internet berdasarkan keywords
         |
         v
4. Report Generator menyintesis semua data menjadi laporan validasi
         |
         v
5. User melihat hasil: skor viabilitas, keywords, pertanyaan, sumber, rekomendasi
         |
         v
6. User bisa bertanya lebih lanjut via chat interaktif
```

---

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| **Frontend** | Vue 3 + Vite + Vue Router + Axios |
| **Backend** | Python Flask + Flask-CORS |
| **AI/LLM** | OpenAI SDK (kompatibel dengan provider manapun) |
| **Web Research** | Serper API (Google Search API) |
| **Package Manager** | uv (Python), npm (Node.js) |
| **Container** | Docker + Docker Compose |
| **Dev Tooling** | Concurrently (frontend + backend bersamaan) |

### Kompatibilitas LLM Provider

OpenAI SDK yang digunakan kompatibel dengan berbagai provider:
- **OpenAI** (GPT-4o, GPT-4o-mini, dll)
- **Alibaba Qwen** (via DashScope API)
- **DeepSeek** (DeepSeek-V2, DeepSeek-Chat)
- Provider lain yang mengikuti format OpenAI API

---

## Arsitektur

```
aivalidmarket/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Configuration from .env
│   │   ├── api/
│   │   │   ├── __init__.py      # Blueprint registration
│   │   │   └── validation.py    # API endpoints
│   │   ├── services/
│   │   │   ├── idea_analyzer.py    # LLM-based idea analysis
│   │   │   ├── web_researcher.py   # Serper API web research
│   │   │   └── report_generator.py # ReACT report generation
│   │   ├── models/
│   │   │   └── task.py          # Task management for async ops
│   │   └── utils/
│   │       ├── llm_client.py    # OpenAI SDK wrapper
│   │       └── logger.py        # Logging utility
│   ├── tests/                   # Pytest unit tests
│   ├── pyproject.toml           # Python dependencies
│   └── run.py                   # Entry point
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue            # Landing page + ide input
│   │   │   ├── ValidationView.vue  # Progress polling
│   │   │   └── ResultsView.vue     # Results + chat
│   │   ├── api/
│   │   │   └── validation.js       # API client
│   │   └── router/
│   │       └── index.js            # Vue Router config
│   ├── package.json
│   └── vite.config.js
├── package.json              # Root scripts (concurrently)
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Prasyarat

Pastikan sudah terinstall di sistem kamu:

- **Node.js** 18+ ([download](https://nodejs.org/))
- **Python** 3.11+ ([download](https://www.python.org/downloads/))
- **uv** - Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))

---

## Instalasi

```bash
# Clone repository
git clone https://github.com/NgajiKripto/AiValidMarket.git
cd AiValidMarket

# Setup environment variables
cp .env.example .env
# Edit .env dengan API keys kamu (lihat bagian Konfigurasi)

# Install semua dependencies (root + frontend + backend)
npm run setup:all
```

---

## Konfigurasi Environment

Buat file `.env` di root project (copy dari `.env.example`):

```env
LLM_API_KEY=your-openai-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
SERPER_API_KEY=your-serper-api-key-here
SECRET_KEY=change-this-in-production
DEBUG=false
```

### Cara Mendapatkan API Keys

| Key | Sumber | Keterangan |
|-----|--------|------------|
| `LLM_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) | Atau provider lain yang kompatibel (Qwen via DashScope, DeepSeek, dll) |
| `SERPER_API_KEY` | [serper.dev](https://serper.dev) | Free tier tersedia: 2500 queries/bulan |

### Menggunakan Provider LLM Lain

Untuk menggunakan provider selain OpenAI, ubah `LLM_BASE_URL` dan `LLM_MODEL_NAME`:

```env
# Contoh: Alibaba Qwen (DashScope)
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# Contoh: DeepSeek
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
```

---

## Menjalankan Aplikasi

### Development Mode

Menjalankan frontend dan backend secara bersamaan:

```bash
npm run dev
```

Atau jalankan secara terpisah:

```bash
# Backend saja
npm run backend

# Frontend saja
npm run frontend
```

### URL Akses

| Service | URL |
|---------|-----|
| Frontend | [http://localhost:3000](http://localhost:3000) |
| Backend API | [http://localhost:5001](http://localhost:5001) |
| Health Check | [http://localhost:5001/health](http://localhost:5001/health) |

---

## Docker

Jalankan seluruh aplikasi menggunakan Docker Compose:

```bash
# Setup environment
cp .env.example .env
# Edit .env dengan API keys

# Build dan jalankan
docker compose up -d

# Lihat logs
docker compose logs -f

# Stop
docker compose down
```

---

## Testing

### Backend Tests

```bash
cd backend && uv run pytest tests/ -v
```

### Frontend Build Check

```bash
cd frontend && npm run build
```

---

## API Endpoints

### POST `/api/validation/validate`

Submit ide untuk validasi (async, mengembalikan task_id).

**Request:**
```json
{
  "idea": "Aplikasi delivery makanan sehat untuk pekerja kantoran di Jakarta"
}
```

**Response:**
```json
{
  "task_id": "uuid-string",
  "message": "Validation started"
}
```

### GET `/api/validation/status/<task_id>`

Cek status dan progress validasi.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "progress": 65,
  "current_step": "Researching market data..."
}
```

### GET `/api/validation/result/<task_id>`

Ambil hasil validasi yang sudah selesai.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "result": {
    "executive_summary": "...",
    "market_viability_score": 7,
    "keywords_analysis": [...],
    "questions_analysis": [...],
    "sources": {...},
    "recommendations": [...]
  }
}
```

### POST `/api/validation/chat`

Chat follow-up dengan AI tentang hasil validasi.

**Request:**
```json
{
  "task_id": "uuid-string",
  "message": "Siapa kompetitor utama di segmen ini?",
  "chat_history": []
}
```

**Response:**
```json
{
  "response": "Berdasarkan hasil validasi, kompetitor utama di segmen ini..."
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "AiValidMarket API"
}
```

---

## Kontribusi

Kontribusi sangat diterima! Berikut cara berkontribusi:

### Langkah-langkah

1. **Fork** repository ini
2. **Clone** fork kamu:
   ```bash
   git clone https://github.com/username-kamu/AiValidMarket.git
   ```
3. **Buat branch** untuk fitur/fix:
   ```bash
   git checkout -b feat/nama-fitur
   ```
4. **Lakukan perubahan** dan pastikan tests tetap pass
5. **Commit** dengan format yang jelas:
   ```bash
   git commit -m "feat: deskripsi perubahan"
   ```
6. **Push** ke fork kamu:
   ```bash
   git push origin feat/nama-fitur
   ```
7. **Buat Pull Request** ke repository utama

### Konvensi Kode

- **Backend**: Flask app factory pattern, Blueprint routing, service layer terpisah
- **Frontend**: Vue 3 Composition API dengan `<script setup>`, brutalist design
- **Commit**: Gunakan prefix (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`)
- **Style**: Ikuti pattern yang sudah ada di codebase

### Area Kontribusi

- Penambahan sumber data baru (marketplace, forum, dll)
- Perbaikan prompt AI untuk analisis yang lebih akurat
- Penambahan bahasa/lokalisasi
- Perbaikan UI/UX
- Penambahan unit test
- Dokumentasi

---

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

<div align="center">

**AiValidMarket** - Validasi ide kamu sebelum eksekusi.

Dibuat dengan Python, Vue.js, dan AI.

Terinspirasi oleh [MiroFish](https://github.com/666ghj/MiroFish)

</div>
