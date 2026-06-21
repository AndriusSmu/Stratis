# 🎯 Stratis | Marketing Command Console

Stratis is a high-performance, dark-themed marketing campaign management engine[cite: 5]. It features a streamlined dual-panel layout: an administrative strategy control matrix on the left, and a real-time data visualization dashboard with live database indexing on the right. 

Built with a lightning-fast asynchronous **FastAPI** backend and an optimized **Vanilla JavaScript** frontend, Stratis implements rigorous Pydantic type-safety and structural UX timeline validation.

---

## ⚡ Key Upgrades

*   **FastAPI & Pydantic Engine**: Upgraded from raw Python sockets to high-throughput ASGI architecture with automatic serialization, native CORS management, and robust schema data validation.
*   **Dual-Panel HUD Layout**: Abandoned vertical layout fatigue in favor of a 2-column tactical control grid tailored for ultrawide desktop environments.
*   **Real-Time Allocation Monitoring**: Aggregates and calculates absolute spend and live operational budgets dynamically.
*   **Timeline Conflict Safeguard**: Front-end validation checks date vectors to block execution logic if a strategy's termination date is configured before its activation date.
*   **Performance Optimization**: Integrated a keystroke debounce layer into the query engine to eliminate interface stutter during system registry filtering.

---

## 🗂️ Project Structure

```text
stratis/
│
├── backend/
│   ├── server.py         # FastAPI application & SQLite pipeline
│   └── campaigns.db      # Automatically initialized SQLite database
│
└── frontend/
    ├── index.html        # App interface & stylized inline SVG 'S' favicon
    ├── styles.css        # Premium dark-slate midnight workspace UI
    └── script.js         # API interface layer, dashboard metrics & validation