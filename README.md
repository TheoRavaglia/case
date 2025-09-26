# Marketing Analytics Dashboard

Marketing dashboard with authentication, filters and role-based access.

## Live Demo
https://marketing-analytics-api-nsfc.onrender.com/docs

## Setup
```bash
git clone https://github.com/TheoRavaglia/case.git && cd case

# Backend
cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --port 8001

# Frontend
cd frontend && npm install && npm run dev
```

## Login
- Admin: `user1@company.com` / `oeiruhn56146`
- User: `user2@company.com` / `908ijofff`

## Tech
FastAPI + React + TypeScript

