from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
import math

class OGUCParameters(BaseModel):
    surface_area: float  # Superficie total del terreno (m²)
    floors: int  # Número de pisos
    max_height: float  # Altura máxima permitida (metros)
    constructibility_coef: float  # Coeficiente de constructibilidad
    occupation_percentage: float  # Porcentaje de ocupación de suelo
    zone_type: str  # Tipo de zona (residencial, comercial, etc.)
    min_dwelling_area: float = 40.0  # Mínimo para vivienda

class CabidaCalculation(BaseModel):
    total_surface: float  # Superficie total del terreno
    max_building_surface: float  # Cabida máxima de edificación
    max_occupation_surface: float  # Superficie máxima de emplazamiento
    allowed_floors: int  # Pisos permitidos
    max_height: float  # Altura máxima permitida
    constructibility_utilization: float  # % de utilización del coeficiente
    dwelling_units_max: int  # Unidades de vivienda máximas
    compliance_status: str  # "APROBADO" o "RECHAZADO"
    rejection_reasons: List[str] = []  # Motivos de rechazo

class OGUCCalculator:
    def __init__(self):
        # Reglas OGUC básicas
        self.min_dwelling_area = 40.0  # m²
        self.max_occupation_by_zone = {
            "residencial": 0.6,
            "comercial": 0.8,
            "industrial": 0.7,
            "mixto": 0.7
        }
        
    def calculate_cabida(self, params: OGUCParameters) -> CabidaCalculation:
        """Calcula la cabida según normativa OGUC"""
        
        # Validaciones básicas
        rejection_reasons = []
        
        # 1. Validar superficie mínima
        if params.surface_area < self.min_dwelling_area:
            rejection_reasons.append(f"Superficie del terreno ({params.surface_area}m²) inferior al mínimo legal ({self.min_dwelling_area}m²)")
        
        # 2. Validar coeficiente de constructibilidad
        if params.constructibility_coef <= 0 or params.constructibility_coef > 3.0:
            rejection_reasons.append(f"Coeficiente de constructibilidad ({params.constructibility_coef}) fuera de rango válido (0.1 - 3.0)")
        
        # 3. Validar altura máxima
        if params.max_height > 50.0:  # Límite razonable para Chile
            rejection_reasons.append(f"Altura máxima ({params.max_height}m) excede límites razonables (50m)")
        
        # 4. Validar porcentaje de ocupación
        max_occupation = self.max_occupation_by_zone.get(params.zone_type.lower(), 0.6)
        if params.occupation_percentage > (max_occupation * 100):
            rejection_reasons.append(f"Porcentaje de ocupación ({params.occupation_percentage}%) excede máximo para zona {params.zone_type} ({max_occupation * 100}%)")
        
        # Cálculos
        max_building_surface = params.surface_area * params.constructibility_coef
        max_occupation_surface = params.surface_area * (params.occupation_percentage / 100)
        
        # Calcular pisos permitidos según altura
        floor_height = 2.6  # Altura estándar por piso en Chile
        allowed_floors_by_height = min(params.floors, int(params.max_height / floor_height))
        
        # Calcular unidades de vivienda máximas
        dwelling_units_max = int(max_building_surface / params.min_dwelling_area)
        
        # Calcular utilización del coeficiente
        if params.surface_area * params.constructibility_coef > 0:
            constructibility_utilization = (max_building_surface / (params.surface_area * params.constructibility_coef)) * 100
        else:
            constructibility_utilization = 0
        
        # Determinar estado de cumplimiento
        compliance_status = "APROBADO" if not rejection_reasons else "RECHAZADO"
        
        return CabidaCalculation(
            total_surface=params.surface_area,
            max_building_surface=max_building_surface,
            max_occupation_surface=max_occupation_surface,
            allowed_floors=allowed_floors_by_height,
            max_height=params.max_height,
            constructibility_utilization=constructibility_utilization,
            dwelling_units_max=dwelling_units_max,
            compliance_status=compliance_status,
            rejection_reasons=rejection_reasons
        )
    
    def validate_dwelling_requirements(self, dwelling_area: float, min_required: float = 40.0) -> bool:
        """Valida si una vivienda cumple con mínimos requeridos"""
        return dwelling_area >= min_required
    
    def calculate_density(self, total_surface: float, building_surface: float) -> float:
        """Calcula densidad de construcción"""
        if total_surface == 0:
            return 0
        return (building_surface / total_surface) * 100
    
    def get_zone_restrictions(self, zone_type: str) -> Dict:
        """Obtiene restricciones específicas por tipo de zona"""
        restrictions = {
            "residencial": {
                "max_height": 23.0,
                "max_constructibility": 2.0,
                "max_occupation": 0.6
            },
            "comercial": {
                "max_height": 30.0,
                "max_constructibility": 3.0,
                "max_occupation": 0.8
            },
            "industrial": {
                "max_height": 25.0,
                "max_constructibility": 2.5,
                "max_occupation": 0.7
            },
            "mixto": {
                "max_height": 28.0,
                "max_constructibility": 2.5,
                "max_occupation": 0.7
            }
        }
        return restrictions.get(zone_type.lower(), restrictions["residencial"])
