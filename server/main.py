from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routes.auth import router as auth_router
from routes.learning import router as learning_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more info
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="NeuroMentor API")

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"Validation error: {exc.errors()}")
    logging.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(learning_router)  # Already has /api/learning prefix

@app.get("/")
def read_root():
    return {"message": "NeuroMentor API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "database": "connected",
            "ai": "ready"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
