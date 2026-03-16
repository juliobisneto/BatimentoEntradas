from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, settings
from app.api import payment_methods, transactions, auth, acquirers
from app.models import acquirer  # noqa: F401 - register models for create_all

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ticket Revenue Reconciliation System",
    description="API for ticket revenue management and reconciliation",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production if needed
    redoc_url="/redoc" if settings.debug else None
)

# CORS - Dynamic origins based on environment
# In production, only allow specified frontend URL
# In development, allow localhost and the configured frontend URL
allowed_origins = [
    settings.frontend_url,
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
]

# Remove duplicates and empty strings
allowed_origins = list(filter(None, set(allowed_origins)))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router)
app.include_router(payment_methods.router)
app.include_router(transactions.router)
app.include_router(acquirers.router)

@app.get("/")
def root():
    return {
        "message": "Ticket Revenue Reconciliation System - API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}


