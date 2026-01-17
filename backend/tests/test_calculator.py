import pytest
from app.core.oguc_calculator import OGUCCalculator, OGUCParameters

class TestOGUCCalculator:
    
    def setup_method(self):
        self.calculator = OGUCCalculator()
    
    def test_basic_calculation_residential(self):
        """Test cálculo básico para zona residencial"""
        params = OGUCParameters(
            surface_area=500.0,
            floors=3,
            max_height=23.0,
            constructibility_coef=1.2,
            occupation_percentage=60.0,
            zone_type="residencial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.total_surface == 500.0
        assert result.max_building_surface == 600.0  # 500 * 1.2
        assert result.max_occupation_surface == 300.0  # 500 * 0.6
        assert result.compliance_status == "APROBADO"
        assert result.dwelling_units_max == 15  # 600 / 40
    
    def test_minimum_surface_rejection(self):
        """Test rechazo por superficie mínima"""
        params = OGUCParameters(
            surface_area=35.0,  # Menor al mínimo legal
            floors=2,
            max_height=15.0,
            constructibility_coef=1.0,
            occupation_percentage=60.0,
            zone_type="residencial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.compliance_status == "RECHAZADO"
        assert any("Superficie del terreno" in reason for reason in result.rejection_reasons)
    
    def test_invalid_constructibility_coefficient(self):
        """Test rechazo por coeficiente inválido"""
        params = OGUCParameters(
            surface_area=500.0,
            floors=3,
            max_height=23.0,
            constructibility_coef=5.0,  # Excede límite razonable
            occupation_percentage=60.0,
            zone_type="residencial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.compliance_status == "RECHAZADO"
        assert any("Coeficiente de constructibilidad" in reason for reason in result.rejection_reasons)
    
    def test_excessive_height(self):
        """Test rechazo por altura excesiva"""
        params = OGUCParameters(
            surface_area=500.0,
            floors=10,
            max_height=60.0,  # Excede límite razonable
            constructibility_coef=1.2,
            occupation_percentage=60.0,
            zone_type="residencial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.compliance_status == "RECHAZADO"
        assert any("Altura máxima" in reason for reason in result.rejection_reasons)
    
    def test_occupation_percentage_limit(self):
        """Test límite de porcentaje de ocupación por zona"""
        params = OGUCParameters(
            surface_area=500.0,
            floors=3,
            max_height=23.0,
            constructibility_coef=1.2,
            occupation_percentage=85.0,  # Excede 60% para residencial
            zone_type="residencial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.compliance_status == "RECHAZADO"
        assert any("Porcentaje de ocupación" in reason for reason in result.rejection_reasons)
    
    def test_commercial_zone_restrictions(self):
        """Test restricciones para zona comercial"""
        params = OGUCParameters(
            surface_area=1000.0,
            floors=5,
            max_height=28.0,
            constructibility_coef=2.5,
            occupation_percentage=75.0,
            zone_type="comercial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.compliance_status == "APROBADO"
        assert result.max_building_surface == 2500.0  # 1000 * 2.5
    
    def test_floor_height_calculation(self):
        """Test cálculo de pisos permitidos por altura"""
        params = OGUCParameters(
            surface_area=500.0,
            floors=10,  # Solicita 10 pisos
            max_height=15.0,  # Pero altura solo permite ~5 pisos
            constructibility_coef=1.2,
            occupation_percentage=60.0,
            zone_type="residencial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.allowed_floors <= 5  # 15m / 2.6m por piso ≈ 5 pisos
    
    def test_zone_restrictions_method(self):
        """Test método de restricciones por zona"""
        restrictions = self.calculator.get_zone_restrictions("residencial")
        
        assert "max_height" in restrictions
        assert "max_constructibility" in restrictions
        assert "max_occupation" in restrictions
        assert restrictions["max_occupation"] == 0.6
    
    def test_density_calculation(self):
        """Test cálculo de densidad"""
        density = self.calculator.calculate_density(500.0, 300.0)
        
        assert density == 60.0  # (300/500) * 100
    
    def test_dwelling_requirements_validation(self):
        """Test validación de requisitos de vivienda"""
        assert self.calculator.validate_dwelling_requirements(50.0) == True
        assert self.calculator.validate_dwelling_requirements(35.0) == False
    
    def test_edge_case_zero_surface(self):
        """Test caso borde con superficie cero"""
        params = OGUCParameters(
            surface_area=0.0,
            floors=1,
            max_height=23.0,
            constructibility_coef=1.0,
            occupation_percentage=60.0,
            zone_type="residencial"
        )
        
        result = self.calculator.calculate_cabida(params)
        
        assert result.compliance_status == "RECHAZADO"
        assert result.max_building_surface == 0.0
