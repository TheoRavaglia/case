# Marketing Analytics Dashboard

Dashboard for marketing campaign analysis with login system, date filters, sorting and role-based access control.

## Setup

```bash
# Clone
git clone https://github.com/TheoRavaglia/case.git && cd case

# Backend
cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --port 8001

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

## Access

- **URL:** http://localhost:5174
- **Credentials:** See `backend/users.csv`
- **API Docs:** http://localhost:8001/docs

## Structure

```
case/
├── backend/    # FastAPI + Python + CSV data
├── frontend/   # React + TypeScript
└── tests/      # Automated tests
```