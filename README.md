# 🎯 Stratis | Marketing Command Console

Stratis is a high-performance, dark-themed marketing campaign management engine. It features a streamlined, high-accessibility dual-panel layout: an administrative strategy control matrix on the left, and a real-time data visualization dashboard with live database indexing on the right. 

Built with an asynchronous FastAPI backend and a responsive Vanilla JavaScript frontend, Stratis provides structural UX timeline validation, instant query filtering, and automatic financial asset calculation out of the box.

---

## 🗂️ Project Structure

stratis/
├── backend/
│   ├── server.py         # FastAPI application & SQLite pipeline
│   └── campaigns.db      # Automatically initialized SQLite database
│
└── frontend/
    ├── index.html        # App interface & stylized inline SVG 'S' favicon
    ├── styles.css        # Premium dark-slate midnight workspace UI
    └── script.js         # API interface layer, dashboard metrics & validation

---

## 🚀 Quick Start Execution

### 1. Initialize the Core Engine
Ensure you have Python 3.8+ installed, then install the necessary production modules:

pip install fastapi uvicorn

Navigate to your backend directory and boot the service pipeline using Uvicorn:

python server.py

The terminal will confirm connection channels are operational:
INFO:     Started server process [12400]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

### 2. Launch the Control Console
To interact with the software, do NOT use the raw backend documentation page. Instead, deploy the user interface using one of the options below:
*   Option A (Recommended): Right-click index.html inside VS Code and select Open with Live Server.
*   Option B: Navigate to the directory in your system file explorer and double-click index.html to run it in your web browser.

---

## 🛠️ API & System Developer Testing
Stratis automatically builds self-documenting technical reference panels. While the server is active, you can monitor raw endpoints, payload schemas, and validation configurations by visiting:

*   Interactive Swagger UI Panel: http://127.0.0.1:8000/docs
*   Alternative ReDoc Panel: http://127.0.0.1:8000/redoc

---

## 🛡️ Data Specification Architecture

Every strategy matrix entry handles the following schema properties under validation:

| Attribute | Data Type | Requirement | System Description |
| :--- | :--- | :--- | :--- |
| name | String | Required | Unique strategic index identifier (1–100 chars). |
| description | String / Null | Optional | Context objectives, operational notes, or channel scopes. |
| budget | Float | Required | Total financial capital assignment (> 0.00). |
| currency | String | Required | Target ledger market token (Defaults to USD). |
| start_date | String (ISO) | Required | Core system activation parameter date. |
| end_date | String (ISO) | Optional | Target campaign termination and lifecycle end date. |
| target_audience | String / Null | Optional | Demographic bracket parameters or user personas. |
| status | String | Required | Current state cycle (Draft, Active, Paused, Completed). |