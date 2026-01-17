from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import time

from app.core.oguc_calculator import OGUCCalculator, OGUCParameters
from app.models.certificate import CertificateData, ValidationError

router = APIRouter()

class ValidationRequest(BaseModel):
    certificate_data: CertificateData
    floors: int
    zone_type: str
    min_dwelling_area: float = 40.0

class ValidationResult(BaseModel):
    is_valid: bool
    validation_score: float  # 0-100
    errors: List[ValidationError]
    warnings: List[ValidationError]
    recommendations: List[str]
    compliance_summary: Dict[str, Any]

@router.post("/compliance", response_model=ValidationResult)
async def validate_compliance(request: ValidationRequest):
    """
    Valida el cumplimiento normativo completo según OGUC
    """
    start_time = time.time()
    
    try:
        errors = []
        warnings = []
        recommendations = []
        
        # Validaciones básicas de datos del certificado
        errors.extend(_validate_certificate_data(request.certificate_data))
        
        # Si hay errores críticos, retornar temprano
        critical_errors = [e for e in errors if e.severity == "error"]
        if critical_errors:
            return ValidationResult(
                is_valid=False,
                validation_score=0,
                errors=errors,
                warnings=warnings,
                recommendations=["Corrija los errores críticos antes de continuar"],
                compliance_summary={"status": "RECHAZADO", "critical_errors": len(critical_errors)}
            )
        
        # Crear parámetros para validación
        params = OGUCParameters(
            surface_area=request.certificate_data.superficie_terreno or 0,
            floors=request.floors,
            max_height=request.certificate_data.altura_maxima or 23.0,
            constructibility_coef=request.certificate_data.coeficiente_constructibilidad or 1.0,
            occupation_percentage=request.certificate_data.porcentaje_ocupacion or 60.0,
            zone_type=request.zone_type,
            min_dwelling_area=request.min_dwelling_area
        )
        
        # Validaciones OGUC
        calculator = OGUCCalculator()
        result = calculator.calculate_cabida(params)
        
        # Procesar resultados del cálculo
        if result.compliance_status == "RECHAZADO":
            for reason in result.rejection_reasons:
                errors.append(ValidationError(
                    field="compliance",
                    message=reason,
                    severity="error"
                ))
        
        # Generar advertencias y recomendaciones
        warnings.extend(_generate_warnings(result, params))
        recommendations.extend(_generate_validation_recommendations(result, params))
        
        # Calcular score de validación
        validation_score = _calculate_validation_score(errors, warnings, result)
        
        # Resumen de cumplimiento
        compliance_summary = {
            "status": result.compliance_status,
            "validation_score": validation_score,
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "max_building_surface": result.max_building_surface,
            "dwelling_units_max": result.dwelling_units_max,
            "constructibility_utilization": result.constructibility_utilization
        }
        
        processing_time = time.time() - start_time
        
        return ValidationResult(
            is_valid=len([e for e in errors if e.severity == "error"]) == 0,
            validation_score=validation_score,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
            compliance_summary=compliance_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en validación: {str(e)}")

@router.post("/quick-validate", response_model=Dict[str, Any])
async def quick_validate(
    surface_area: float,
    floors: int,
    zone_type: str = "residencial",
    constructibility_coef: float = 1.0,
    occupation_percentage: float = 60.0,
    max_height: float = 23.0
):
    """
    Validación rápida sin certificado
    """
    try:
        params = OGUCParameters(
            surface_area=surface_area,
            floors=floors,
            max_height=max_height,
            constructibility_coef=constructibility_coef,
            occupation_percentage=occupation_percentage,
            zone_type=zone_type
        )
        
        calculator = OGUCCalculator()
        result = calculator.calculate_cabida(params)
        
        return {
            "is_valid": result.compliance_status == "APROBADO",
            "status": result.compliance_status,
            "rejection_reasons": result.rejection_reasons,
            "validation_score": 100 if result.compliance_status == "APROBADO" else 0,
            "summary": {
                "max_building_surface": result.max_building_surface,
                "dwelling_units_max": result.dwelling_units_max,
                "allowed_floors": result.allowed_floors
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en validación rápida: {str(e)}")

def _validate_certificate_data(certificate_data: CertificateData) -> List[ValidationError]:
    """Valida datos básicos del certificado"""
    errors = []
    
    if not certificate_data.superficie_terreno:
        errors.append(ValidationError(
            field="superficie_terreno",
            message="No se pudo extraer la superficie del terreno",
            severity="error"
        ))
    elif certificate_data.superficie_terreno < 40:
        errors.append(ValidationError(
            field="superficie_terreno",
            message=f"Superficie del terreno ({certificate_data.superficie_terreno}m²) inferior al mínimo legal (40m²)",
            severity="error"
        ))
    
    if not certificate_data.rol:
        errors.append(ValidationError(
            field="rol",
            message="No se pudo extraer el rol del predio",
            severity="warning"
        ))
    
    if not certificate_data.comuna:
        errors.append(ValidationError(
            field="comuna",
            message="No se pudo extraer la comuna",
            severity="warning"
        ))
    
    return errors

def _generate_warnings(result, params: OGUCParameters) -> List[ValidationError]:
    """Genera advertencias basadas en el resultado"""
    warnings = []
    
    if result.constructibility_utilization < 50:
        warnings.append(ValidationError(
            field="optimization",
            message=f"Baja utilización del coeficiente de constructibilidad ({result.constructibility_utilization:.1f}%)",
            severity="warning"
        ))
    
    if result.allowed_floors < params.floors:
        warnings.append(ValidationError(
            field="height",
            message=f"Altura máxima permite solo {result.allowed_floors} pisos ({params.floors} solicitados)",
            severity="warning"
        ))
    
    if not params.coeficiente_constructibilidad or params.coeficiente_constructibilidad == 1.0:
        warnings.append(ValidationError(
            field="constructibility",
            message="Usando coeficiente de constructibilidad por defecto (1.0)",
            severity="info"
        ))
    
    return warnings

def _generate_validation_recommendations(result, params: OGUCParameters) -> List[str]:
    """Genera recomendaciones basadas en la validación"""
    recommendations = []
    
    if result.compliance_status == "APROBADO":
        recommendations.append("✅ El proyecto cumple con las normativas OGUC básicas")
        recommendations.append(f"📊 Cabida máxima permitida: {result.max_building_surface:.1f}m²")
        recommendations.append(f"🏠 Unidades de vivienda máximas: {result.dwelling_units_max}")
        
        if result.constructibility_utilization < 70:
            recommendations.append("💡 Considere optimizar el uso del coeficiente de constructibilidad")
    else:
        recommendations.append("❌ El proyecto no cumple con las normativas OGUC")
        recommendations.append("📋 Revise los motivos de rechazo indicados")
        recommendations.append("🔄 Realice los ajustes necesarios y vuelva a validar")
    
    return recommendations

def _calculate_validation_score(errors: List[ValidationError], warnings: List[ValidationError], result) -> float:
    """Calcula un score de validación de 0-100"""
    if any(e.severity == "error" for e in errors):
        return 0
    
    base_score = 100
    
    # Restar puntos por advertencias
    warning_penalty = len(warnings) * 10
    base_score -= warning_penalty
    
    # Restar puntos por baja utilización
    if result.constructibility_utilization < 50:
        base_score -= 20
    elif result.constructibility_utilization < 70:
        base_score -= 10
    
    return max(0, base_score)
