# MANAK AI

**From Product to Compliance**

An AI-powered intelligent assistant for Indian Standards and BIS services for industries and consumers.

## Disclaimer

MANAK AI provides informational and decision-support guidance based on its indexed knowledge sources. It is not an official BIS certification authority, legal advisor, or substitute for official BIS processes. Users should verify critical compliance decisions with authoritative sources and appropriate professionals.

## Features

- AI Standards Search
- Compliance Passport
- Document Analysis
- Smart Lab Matcher
- Knowledge Graph
- Multilingual AI

## Technology Stack

### Backend
- Python 3.12+
- FastAPI
- PostgreSQL with pgvector
- Redis
- Alembic
- SQLAlchemy 2

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query

### AI
- LLM abstraction (OpenAI, etc.)
- Embedding abstraction
- RAG pipeline
- Vector search with pgvector

## Project Structure

```
manak-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   ├── ai/
│   │   └── security/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   └── api/
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── demo/
│   ├── raw/
│   └── processed/
├── prompts/
├── docker-compose.yml
└── .env.example
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Node.js 20+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your settings
3. Run:

```bash
docker-compose up -d
```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

### Local Development

#### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp ../.env.example .env
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

## User Roles

- ADMIN
- MANUFACTURER
- MSME
- CONSUMER
- LABORATORY
- STUDENT
- COMPLIANCE_OFFICER

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/organization` - Create organization

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

The application is configured for deployment on Render:

- React Frontend → Render Static Site
- FastAPI Backend → Render Web Service
- PostgreSQL → Render PostgreSQL
- Redis → Render-compatible Redis solution

Configure environment variables securely in your deployment platform.

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Role-based access control (RBAC)
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

## License

This project is developed for hackathon purposes. Please ensure compliance with BIS and government regulations when using any official standards data.

## Support

For issues and questions, please refer to the project documentation or contact the development team.
