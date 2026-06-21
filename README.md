# 🎯 Stratis | Marketing Campaign Manager

Stratis is a marketing campaign manager built with a FastAPI backend and a Vanilla JS frontend. It lets you create, track, and manage campaigns with real-time filtering and automatic budget calculations — no external frameworks, no third-party libraries.

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

- **Option A (Recommended):** Right-click `index.html` in VS Code → Open with Live Server
- **Option B:** Double-click `index.html` to open it in your browser

---

## 🛠️ API Docs

While the server is running, you can explore the API at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 📋 Campaign Fields

| Field            | Type          | Required | Description                              |
| :--------------- | :------------ | :------- | :--------------------------------------- |
| name             | String        | Yes      | Campaign name (1–100 chars)              |
| description      | String / Null | No       | Optional notes                           |
| budget           | Float         | Yes      | Budget amount (must be > 0)              |
| currency         | String        | Yes      | Currency code (default: USD)             |
| start_date       | String (ISO)  | Yes      | Start date                               |
| end_date         | String (ISO)  | No       | End date                                 |
| target_audience  | String / Null | No       | Target audience description              |
| status           | String        | Yes      | Draft, Active, Paused, or Completed      |
