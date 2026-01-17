from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CertificateRequest(BaseModel):
    """Modelo para solicitud de procesamiento de certificado"""
    floors: int = Field(..., ge=1, le=50, description="Número de pisos deseados")
    zone_type: str = Field(..., description="Tipo de zona (residencial, comercial, industrial, mixto)")
    min_dwelling_area: float = Field(default=40.0, ge=20.0, description="Superficie mínima por vivienda (m²)")

class CertificateResponse(BaseModel):
    """Modelo para respuesta de procesamiento de certificado"""
    success: bool
    message: str
    certificate_data: Optional[dict] = None
    calculation_result: Optional[dict] = None
    validation_status: Optional[str] = None
    rejection_reasons: Optional[List[str]] = None
    processing_time: Optional[float] = None

class CertificateData(BaseModel):
    """Datos extraídos del certificado"""
    rol: Optional[str] = None
    comuna: Optional[str] = None
    superficie_terreno: Optional[float] = None
    direccion: Optional[str] = None
    nombre_propietario: Optional[str] = None
    uso_suelo: Optional[str] = None
    zona: Optional[str] = None
    altura_maxima: Optional[float] = None
    coeficiente_constructibilidad: Optional[float] = None
    porcentaje_ocupacion: Optional[float] = None
    raw_text: Optional[str] = None
    additional_data: Optional[dict] = None

class CalculationResult(BaseModel):
    """Resultado del cálculo de cabidas"""
    total_surface: float
    max_building_surface: float
    max_occupation_surface: float
    allowed_floors: int
    max_height: float
    constructibility_utilization: float
    dwelling_units_max: int
    compliance_status: str
    rejection_reasons: List[str] = []
    recommendations: List[str] = []

class ValidationError(BaseModel):
    """Modelo para errores de validación"""
    field: str
    message: str
    severity: str  # "error", "warning", "info"

class ProcessingLog(BaseModel):
    """Log del proceso de cálculo"""
    timestamp: datetime
    step: str
    status: str
    details: Optional[str] = None
    processing_time_ms: Optional[float] = None
