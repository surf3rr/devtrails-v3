# ParametricGuard 🛡️

Hackathon-ready parametric insurance demo. FastAPI backend + React/Tailwind frontend.

---

## Project Structure

```
parametricguard/
├── backend/
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── public/index.html
    ├── src/
    │   ├── index.js
    │   ├── index.css
    │   ├── App.js
    │   └── pages/
    │       ├── Login.js
    │       └── Dashboard.js
    ├── package.json
    ├── tailwind.config.js
    └── postcss.config.js
```

---

## 1 — Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API will be live at **http://localhost:8000**

Swagger docs: http://localhost:8000/docs

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /user | User profile + wallet |
| GET | /policy | Policy details |
| GET | /events | Live rainfall & trigger status |
| GET | /claims | Payout history |
| POST | /buy-policy | Activate/renew policy |
| GET | /premium/calculate | Premium calculator |

> `/events` returns a random rainfall value on each call — refresh to see the payout trigger flip on/off.

---

## 2 — Frontend (React + Tailwind)

```bash
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npm start
```

App opens at **http://localhost:3000**

### Login
- Email: `arjun@example.com`  
- Password: `password`  
- (Any value works — auth is mocked)

---

## Features

| Feature | Detail |
|---------|--------|
| 🌗 Dark/Light toggle | Persistent per session, smooth transition |
| 👤 User summary card | Name, location, wallet balance, policy status |
| 📄 Policy card | Premium, coverage, active days, Buy button |
| 🌧️ Event status | Live rainfall bar, threshold indicator, payout alert |
| 💸 Claims history | Date, event type, amount, status badge |
| 🔄 Auto-refresh | Polls backend every 8 seconds |
| 📱 Responsive | Works on mobile and desktop |

---

## Demo Tips

- Hit **Buy / Renew Policy** to see wallet deduction update
- The `/events` endpoint randomises rainfall — keep refreshing until `rainfall_mm > 80` triggers the red payout card
- Toggle dark ↔ light mid-demo for visual impact

---

## Tech Stack

- **Frontend**: React 18, React Router v6, Tailwind CSS 3, DM Sans + Space Mono fonts  
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2  
- **Mock data**: In-memory state (no DB needed for the demo)
