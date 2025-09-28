# Marketing Analytics Dashboard

A full-stack web application for marketing data analysis with JWT authentication, role-based access control, and advanced data filtering capabilities.

## Technical Overview

This project demonstrates a complete marketing analytics solution built with modern web technologies. The application processes large datasets (1.3M+ records) with efficient pagination, provides secure authentication, and implements role-based permissions for different user types.

**Key Features:**
- JWT-based authentication system
- Role-based access control (Admin/User permissions)
- Large dataset processing with smart pagination
- Advanced filtering (date ranges, search, sorting)
- Real-time data visualization
- Production-ready cloud deployment

**Architecture:**
- **Backend:** FastAPI with modular architecture, JWT tokens, CSV data processing
- **Frontend:** React with TypeScript, responsive design, real-time updates
- **Database:** CSV-based data storage with optimized loading
- **Deployment:** Cloud-hosted API on Render.com with local development support

## Cloud Backend API

The backend is deployed and running on Render.com:

- **Main API:** https://marketing-analytics-api-nsfc.onrender.com/
- **API Documentation:** https://marketing-analytics-api-nsfc.onrender.com/docs
- **Health Check:** https://marketing-analytics-api-nsfc.onrender.com/health
- **API Endpoints:** https://marketing-analytics-api-nsfc.onrender.com/api

## Quick Start

```bash
git clone https://github.com/TheoRavaglia/case.git
cd case

# Frontend (automatically connects to cloud backend)
cd frontend
npm install
npm run dev

# Backend (optional - for local development)
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001
```

**Note:** The frontend is pre-configured to use the cloud backend. Just run `npm run dev` to start testing immediately.

## Test Credentials

- **Admin User:** `user1@company.com` / `oeiruhn56146`
- **Regular User:** `user2@company.com` / `908ijofff`

Admin users can view all columns including cost data, while regular users have restricted access.

## Technology Stack

- **Backend:** FastAPI, Python, JWT Authentication, Uvicorn
- **Frontend:** React 18, TypeScript, Vite, Modern CSS
- **Data Processing:** Pandas, CSV handling, Smart pagination
- **Deployment:** Render.com (Backend), Local development (Frontend)
- **Testing:** Pytest with comprehensive test coverage

