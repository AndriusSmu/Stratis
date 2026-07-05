# 🎯 Stratis | Marketing Campaign Manager

Stratis is a full-stack marketing campaign manager built with a FastAPI backend and a Vanilla JS frontend. It supports JWT authentication, campaign tracking with budget calculations, AI-powered brief generation, and portfolio health insights.

---

## 🗂️ Project Structure

```
Stratis/
├── backend/
│   ├── app/
│   │   ├── main.py              # App entry point, middleware, route registration
│   │   ├── config.py            # Environment config
│   │   ├── database/            # DB connection and repositories
│   │   ├── models/              # Pydantic models (Campaign, User)
│   │   ├── schemas/             # Request/response schemas
│   │   ├── routers/             # Route handlers (auth, campaigns, ai, dashboard, analytics)
│   │   ├── services/            # Business logic (CampaignService, AIService, AuthService)
│   │   ├── middleware/          # JWT auth middleware
│   │   └── exceptions/          # Custom exceptions and handlers
│   ├── tests/                   # Pytest test suite
│   ├── requirements.txt
│   └── run.py                   # Server entry point
└── frontend/
    ├── index.html               # Main UI
    ├── styles.css               # Styling
    └── script.js                # Client-side logic and API calls
```

---

## 🚀 Quick Start

### 1. Set up the backend

Make sure you have Python 3.8+ installed. Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# or: source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder (see `.env.example` for reference):

```
SECRET_KEY=your-secret-key
```

Start the server:

```bash
python run.py
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Open the frontend

- **Option A (Recommended):** Right-click `index.html` in VS Code → **Open with Live Server**
- **Option B:** Double-click `index.html` to open it in your browser

> ⚠️ Use Live Server for full functionality. Opening via `file://` will block AI features due to CORS restrictions.

---

## 🤖 AI Features (optional)

Stratis includes two AI-powered features running locally via [Ollama](https://ollama.com) — no API keys, no cloud, no costs.

- **Campaign brief generator** — type a name and audience, AI fills in description, tags, and goals
- **Portfolio insights** — AI analyzes your campaigns and highlights what's healthy, overspent, or expired

### Setup

1. Download and install Ollama from [ollama.com](https://ollama.com)
2. Pull the model:

```bash
ollama pull llama3.2
```

3. Ollama starts automatically after installation. If needed:

```bash
ollama serve
```

> AI features are optional. The app works fully without Ollama — AI buttons will show an error if it's not running.

---

## 🛠️ API Docs

While the server is running:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 🧪 Running Tests

```bash
cd backend
pytest
```

---

## 📋 Campaign Fields

| Field           | Type          | Required | Description                         |
| :-------------- | :------------ | :------- | :---------------------------------- |
| name            | String        | Yes      | Campaign name (1–100 chars)         |
| description     | String / Null | No       | Optional description                |
| budget          | Float         | Yes      | Budget amount (must be > 0)         |
| spent           | Float         | No       | Amount already spent                |
| currency        | String        | Yes      | USD, EUR, or GBP (default: USD)     |
| start_date      | String (ISO)  | Yes      | Start date                          |
| end_date        | String (ISO)  | No       | End date                            |
| target_audience | String / Null | No       | Target audience description         |
| status          | String        | Yes      | Draft, Active, Paused, or Completed |
| owner           | String / Null | No       | Owner or responsible person         |
| tags            | List / Null   | No       | Comma-separated tags                |
| assets          | String / Null | No       | Links to briefs, creatives, etc.    |
| notes           | String / Null | No       | Notes or results                    |
