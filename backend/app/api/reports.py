from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
from typing import Dict, Any, List

from app.core.report_generator import ReportGenerator
from app.models.certificate import CertificateData, CalculationResult

router = APIRouter()

class ReportRequest(BaseModel):
    certificate_data: CertificateData
    calculation_result: CalculationResult
    parameters: Dict[str, Any]

class SummaryReportRequest(BaseModel):
    calculations: List[Dict[str, Any]]
    project_names: List[str] = None

@router.post("/generate-pdf")
async def generate_cabida_report(request: ReportRequest):
    """
    Genera reporte PDF completo del cálculo de cabidas
    """
    try:
        report_generator = ReportGenerator()
        
        # Generar PDF
        pdf_content = report_generator.generate_cabida_report(
            certificate_data=request.certificate_data.model_dump(),
            calculation_result=request.calculation_result.model_dump(),
            parameters=request.parameters
        )
        
        # Retornar PDF como streaming response
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=informe_cabida_oguc.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte PDF: {str(e)}")

@router.post("/generate-summary")
async def generate_summary_report(request: SummaryReportRequest):
    """
    Genera reporte resumen de múltiples cálculos
    """
    try:
        report_generator = ReportGenerator()
        
        # Preparar datos para el resumen
        calculations_with_names = []
        for i, calc in enumerate(request.calculations):
            calc_data = calc.copy()
            if request.project_names and i < len(request.project_names):
                calc_data['project_name'] = request.project_names[i]
            else:
                calc_data['project_name'] = f'Proyecto {i+1}'
            calculations_with_names.append(calc_data)
        
        # Generar PDF resumen
        pdf_content = report_generator.generate_summary_report(calculations_with_names)
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resumen_calculos_cabida.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte resumen: {str(e)}")

@router.get("/report-templates")
async def get_report_templates():
    """
    Retorna información sobre las plantillas de reporte disponibles
    """
    return {
        "available_reports": {
            "cabida_report": {
                "name": "Informe de Cálculo de Cabidas",
                "description": "Reporte completo con datos del certificado, parámetros, resultados y recomendaciones",
                "sections": [
                    "Datos del Certificado",
                    "Parámetros de Cálculo", 
                    "Resultados del Cálculo",
                    "Estado de Cumplimiento",
                    "Recomendaciones",
                    "Información Legal"
                ]
            },
            "summary_report": {
                "name": "Reporte Resumen",
                "description": "Reporte comparativo de múltiples cálculos de cabida",
                "format": "Tabla resumen por proyecto"
            }
        },
        "output_formats": ["PDF"],
        "customization_options": {
            "include_legal_info": True,
            "include_recommendations": True,
            "company_logo": False,  # Futura implementación
            "custom_watermark": False  # Futura implementación
        }
    }

@router.post("/preview-report")
async def preview_report_data(request: ReportRequest):
    """
    Retorna vista previa de los datos que irán en el reporte (sin generar PDF)
    """
    try:
        # Preparar datos de vista previa
        preview_data = {
            "certificate_info": {
                "rol": request.certificate_data.rol,
                "direccion": request.certificate_data.direccion,
                "comuna": request.certificate_data.comuna,
                "superficie_terreno": request.certificate_data.superficie_terreno
            },
            "calculation_summary": {
                "compliance_status": request.calculation_result.compliance_status,
                "max_building_surface": request.calculation_result.max_building_surface,
                "dwelling_units_max": request.calculation_result.dwelling_units_max,
                "allowed_floors": request.calculation_result.allowed_floors
            },
            "parameters": request.parameters,
            "rejection_reasons": request.calculation_result.rejection_reasons,
            "recommendations": request.calculation_result.recommendations,
            "estimated_pages": 2 if request.calculation_result.rejection_reasons else 1
        }
        
        return {
            "success": True,
            "preview": preview_data,
            "report_ready": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando vista previa: {str(e)}")
