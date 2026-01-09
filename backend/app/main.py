"""
FastAPI Application - BodyVision Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import pose

app = FastAPI(
    title="BodyVision API",
    description="API para análise de poses de fisiculturismo",
    version="1.0.0"
)

# CORS - Permite requisições do Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra rotas
app.include_router(pose.router, prefix="/api/v1/pose", tags=["pose"])


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "BodyVision API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

