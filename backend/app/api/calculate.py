from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
from typing import Dict, Any

from app.core.oguc_calculator import OGUCCalculator, OGUCParameters, CabidaCalculation
from app.models.certificate import CertificateData, CalculationResult

router = APIRouter()

class CalculationRequest(BaseModel):
    certificate_data: CertificateData
    floors: int
    zone_type: str
    min_dwelling_area: float = 40.0

@router.post("/cabida", response_model=CalculationResult)
async def calculate_cabida(request: CalculationRequest):
    """
    Calcula la cabida según normativa OGUC basado en datos del certificado
    """
    start_time = time.time()
    
    try:
        # Validar datos mínimos requeridos
        if not request.certificate_data.superficie_terreno:
            raise HTTPException(
                status_code=400, 
                detail="No se pudo extraer la superficie del terreno del certificado"
            )
        
        # Crear parámetros para el cálculo
        params = OGUCParameters(
            surface_area=request.certificate_data.superficie_terreno,
            floors=request.floors,
            max_height=request.certificate_data.altura_maxima or 23.0,
            constructibility_coef=request.certificate_data.coeficiente_constructibilidad or 1.0,
            occupation_percentage=request.certificate_data.porcentaje_ocupacion or 60.0,
            zone_type=request.zone_type,
            min_dwelling_area=request.min_dwelling_area
        )
        
        # Realizar cálculo
        calculator = OGUCCalculator()
        result = calculator.calculate_cabida(params)
        
        # Generar recomendaciones
        recommendations = []
        if result.compliance_status == "RECHAZADO":
            recommendations.extend(_generate_rejection_recommendations(result, params))
        else:
            recommendations.extend(_generate_optimization_recommendations(result, params))
        
        processing_time = time.time() - start_time
        
        return CalculationResult(
            total_surface=result.total_surface,
            max_building_surface=result.max_building_surface,
            max_occupation_surface=result.max_occupation_surface,
            allowed_floors=result.allowed_floors,
            max_height=result.max_height,
            constructibility_utilization=result.constructibility_utilization,
            dwelling_units_max=result.dwelling_units_max,
            compliance_status=result.compliance_status,
            rejection_reasons=result.rejection_reasons,
            recommendations=recommendations
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo de cabida: {str(e)}")

@router.post("/quick-calculate", response_model=Dict[str, Any])
async def quick_calculate(
    surface_area: float,
    floors: int,
    zone_type: str = "residencial",
    constructibility_coef: float = 1.0,
    occupation_percentage: float = 60.0,
    max_height: float = 23.0
):
    """
    Cálculo rápido sin certificado (para pruebas y demostración)
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
            "success": True,
            "result": result.model_dump(),
            "parameters": params.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo rápido: {str(e)}")

@router.get("/zone-restrictions/{zone_type}")
async def get_zone_restrictions(zone_type: str):
    """
    Obtiene restricciones específicas por tipo de zona
    """
    try:
        calculator = OGUCCalculator()
        restrictions = calculator.get_zone_restrictions(zone_type)
        
        return {
            "zone_type": zone_type,
            "restrictions": restrictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo restricciones: {str(e)}")

def _generate_rejection_recommendations(result: CabidaCalculation, params: OGUCParameters) -> list:
    """Genera recomendaciones para casos de rechazo"""
    recommendations = []
    
    if "Superficie del terreno" in str(result.rejection_reasons):
        recommendations.append(
            "Verifique que la superficie del terreno sea correcta. "
            "El mínimo legal para vivienda en Chile es de 40m²."
        )
    
    if "Coeficiente de constructibilidad" in str(result.rejection_reasons):
        recommendations.append(
            "Revise el coeficiente de constructibilidad. "
            "Valores típicos van desde 0.5 hasta 3.0 según la zona."
        )
    
    if "Altura máxima" in str(result.rejection_reasons):
        recommendations.append(
            "Verifique la altura máxima permitida. "
            "Considere reducir el número de pisos o consultar el plano regulador local."
        )
    
    if "Porcentaje de ocupación" in str(result.rejection_reasons):
        recommendations.append(
            "Ajuste el porcentaje de ocupación de suelo según el tipo de zona. "
            "Valores típicos: Residencial 60%, Comercial 80%."
        )
    
    return recommendations

def _generate_optimization_recommendations(result: CabidaCalculation, params: OGUCParameters) -> list:
    """Genera recomendaciones de optimización para casos aprobados"""
    recommendations = []
    
    if result.constructibility_utilization < 70:
        recommendations.append(
            f"Está utilizando solo el {result.constructibility_utilization:.1f}% del coeficiente de constructibilidad. "
            "Podría considerar aumentar la superficie de edificación."
        )
    
    if result.allowed_floors < params.floors:
        recommendations.append(
            f"Según la altura máxima, solo puede construir {result.allowed_floors} pisos "
            f"en lugar de los {params.floors} solicitados."
        )
    
    if result.dwelling_units_max > 1 and params.min_dwelling_area > 40:
        recommendations.append(
            f"Podría construir hasta {result.dwelling_units_max} unidades de vivienda. "
            "Considere subdividir para mayor rentabilidad."
        )
    
    return recommendations
