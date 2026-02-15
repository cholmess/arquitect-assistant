from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import time
from typing import Optional
import os

from app.core.pdf_processor import PDFProcessor, CertificateData
from app.core.config import settings

router = APIRouter()

@router.post("/certificate", response_model=dict)
async def upload_certificate(
    file: UploadFile = File(...),
    floors: int = Form(...),
    zone_type: str = Form(...),
    min_dwelling_area: float = Form(default=40.0)
):
    """
    Sube y procesa un Certificado de Informaciones Previas
    """
    start_time = time.time()
    
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato de archivo no permitido. Extensiones permitidas: {settings.allowed_extensions}"
            )
        
        # Validar tamaño
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Procesar archivo
        processor = PDFProcessor()
        certificate_data = processor.process_file(file_content, file.filename)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "message": "Certificado procesado exitosamente",
            "certificate_data": certificate_data.dict(),
            "processing_time": processing_time,
            "parameters": {
                "floors": floors,
                "zone_type": zone_type,
                "min_dwelling_area": min_dwelling_area
            }
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {str(e)}")

@router.post("/validate-format", response_model=dict)
async def validate_certificate_format(file: UploadFile = File(...)):
    """
    Valida si un archivo corresponde a un Certificado de Informaciones Previas válido
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo")
        
        file_content = await file.read()
        
        processor = PDFProcessor()
        
        # Determinar tipo de archivo y extraer texto
        if file.filename.lower().endswith('.pdf'):
            text = processor.extract_text_from_pdf(file_content)
        elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            text = processor.extract_text_from_image(file_content)
        else:
            return {
                "valid": False,
                "message": "Formato de archivo no soportado",
                "supported_formats": settings.allowed_extensions
            }
        
        # Validar formato
        is_valid = processor.validate_certificate_format(text)
        
        # Extraer datos básicos para preview
        preview_data = {}
        if is_valid:
            preview_data = processor.extract_certificate_data(text).dict()
        
        return {
            "valid": is_valid,
            "message": "Formato válido" if is_valid else "No parece ser un Certificado de Informaciones Previas",
            "preview_data": preview_data if is_valid else None
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validando archivo: {str(e)}"
        }

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Retorna los formatos de archivo soportados
    """
    return {
        "supported_formats": settings.allowed_extensions,
        "max_file_size_mb": settings.max_file_size / (1024 * 1024),
        "description": "Se aceptan Certificados de Informaciones Previas en formato PDF o imagen"
    }
