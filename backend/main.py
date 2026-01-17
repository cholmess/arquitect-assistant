from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.api import upload, calculate, validate, reports
from app.core.config import settings

app = FastAPI(
    title="Arquitect Assistant API",
    description="Sistema automatizado de cálculo de cabidas OGUC",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(calculate.router, prefix="/api/v1/calculate", tags=["calculate"])
app.include_router(validate.router, prefix="/api/v1/validate", tags=["validate"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "Arquitect Assistant API - Sistema de Cálculo de Cabidas OGUC"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
