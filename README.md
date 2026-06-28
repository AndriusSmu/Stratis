# 🎯 Stratis | Marketing Campaign Manager

Stratis is a marketing campaign manager built with a FastAPI backend and a Vanilla JS frontend. It lets you create, track, and manage campaigns with real-time filtering, automatic budget calculations, and AI-powered campaign briefs — no external frameworks, no third-party dependencies.

---

## 🗂️ Project Structure

```
Stratis/
├── backend/
│   └── server.py        # FastAPI server and database logic
└── frontend/
    ├── index.html       # Main UI
    ├── styles.css       # Styling
    └── script.js        # Client-side logic and API calls
```

---

## 🚀 Quick Start

### 1. Start the backend

Make sure you have Python 3.8+ installed, then:

```bash
pip install fastapi uvicorn
```

Navigate to the `backend` folder and run:

```bash
python server.py
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Open the frontend

- **Option A (Recommended):** Right-click `index.html` in VS Code → **Open with Live Server**
- **Option B:** Double-click `index.html` to open it in your browser

> ⚠️ If you use Option B, AI features won't work due to browser CORS restrictions. Use Live Server for full functionality.

---

## 🤖 AI Features (optional)

Stratis includes two AI-powered features powered by [Ollama](https://ollama.com) running locally:

- **Campaign brief generator** — enter a campaign name and target audience, click Generate, and AI fills in the description, tags, and notes
- **Portfolio insights** — click "Analyze campaigns" in the sidebar to get an AI summary of your campaign portfolio health

### Setup

1. Download and install Ollama from [ollama.com](https://ollama.com)
2. Pull the model:

```bash
ollama pull llama3.2
```

3. Ollama runs automatically in the background after installation. If needed, start it manually:

```bash
ollama serve
```

> AI features are optional. The app works fully without Ollama — AI buttons will show an error if Ollama is not running.

---

## 🛠️ API Docs

While the server is running, you can explore the API at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

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
