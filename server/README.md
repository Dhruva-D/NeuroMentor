# NeuroMentor Backend

FastAPI backend with MongoDB for authentication.

## Setup

1. Install Python dependencies:
```bash
cd server
pip install -r requirements.txt
```

2. The `.env` file is already configured with MongoDB Atlas connection.

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

**POST /api/auth/signup**
- Register a new user
- Body: `{ "name": "string", "class_name": "string", "email": "string", "password": "string" }`

**POST /api/auth/login**
- Login with email and password
- Body: `{ "email": "string", "password": "string" }`
- Returns: `{ "access_token": "string", "token_type": "bearer" }`

## Project Structure

```
server/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── database.py          # MongoDB connection
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── models/
│   └── schemas.py       # Pydantic models
├── routes/
│   └── auth.py          # Authentication routes
└── utils/
    └── auth.py          # Password hashing and JWT utilities
```
