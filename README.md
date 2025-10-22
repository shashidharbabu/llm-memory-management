# Assignment 06 – Distributed Systems  
Task Management API (Node.js + MongoDB) & AI Memory Service (FastAPI + Ollama)

## Project Structure
```
Assignment06/
├── src/                  # Part 1 – Task Manager API (Node.js/Express)
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   └── server.js
└── Part2/                # Part 2 – AI memory service (FastAPI)
    ├── app/
    ├── static/
    └── tests & setup files
```

## Part 1 – Task Management REST API
- **Stack:** Node.js, Express, Mongoose, MongoDB.
- **Features:** CRUD endpoints, validation, CORS, health check.
- **Run:**
  ```bash
  cd src
  npm install
  npm start
  ```
- **Environment:**
  ```
  MONGODB_URI=<your MongoDB URI>
  PORT=3000
  ```
- **Endpoints:** `POST/GET/PUT/DELETE /api/tasks`, `GET /health`
- **Deliverables:** screenshots of CRUD calls + MongoDB Compass.

## Part 2 – AI Memory FastAPI Service
- **Stack:** FastAPI, Motor (MongoDB), Ollama LLM.
- **Behavior:** short-term, long-term, episodic memory using shared MongoDB.
- **Run:**
  ```bash
  cd Part2
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload
  ```
- **Environment (.env in Part2):**
  ```
  MONGODB_URI=mongodb://localhost:27017
  DATABASE_NAME=assignment06
  OLLAMA_BASE_URL=http://localhost:11434
  CHAT_MODEL=phi3:mini
  EMBED_MODEL=nomic-embed-text
  SHORT_TERM_N=10
  SUMMARIZE_EVERY_USER_MSGS=4
  EPISODIC_TOP_K=5
  ```
- **Endpoints:**  
  - `POST /api/chat`  
  - `GET /api/memory/{user_id}`  
  - `GET /api/aggregate/{user_id}`  
  - Static UI at `/static/index.html`
- **Tests:** see `Part2/test_api.py`, `test_complete.py`, `test_ollama.py`.

## MongoDB Collections
- `tasks` (Part 1)  
- `messages`, `summaries`, `episodes` (Part 2)

## Screenshots (to capture)
1. Part 1 CRUD operations + Compass view of `tasks`.
2. Part 2 chat interaction, `/api/memory`, `/api/aggregate`, Compass views for `messages`, `summaries`, `episodes`.

## Local Git Workflow
```bash
git add README.md
git commit -m "Add project README"
git push origin <your-branch>
```

## Troubleshooting
- Ensure MongoDB & Ollama services are running locally.
- Check `.env` files for correct URIs and model names.
- Review logs (`npm start` or `uvicorn ... --reload`) for runtime errors.
