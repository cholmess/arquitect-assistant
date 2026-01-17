from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
from typing import Dict, List, Any

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el reporte"""
        # Estilo para título
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Estilo para subtítulos
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        )
        
        # Estilo para texto normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        # Estilo para resultados (aprobado/rechazado)
        self.result_style = ParagraphStyle(
            'ResultStyle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            alignment=TA_CENTER
        )
    
    def generate_cabida_report(self, 
                              certificate_data: Dict[str, Any],
                              calculation_result: Dict[str, Any],
                              parameters: Dict[str, Any]) -> bytes:
        """Genera reporte PDF completo de cálculo de cabidas"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Título del reporte
        story.append(Paragraph("INFORME DE CÁLCULO DE CABIDAS OGUC", self.title_style))
        story.append(Spacer(1, 20))
        
        # Información del certificado
        story.append(Paragraph("DATOS DEL CERTIFICADO DE INFORMACIONES PREVIAS", self.subtitle_style))
        story.append(self._create_certificate_table(certificate_data))
        story.append(Spacer(1, 20))
        
        # Parámetros de cálculo
        story.append(Paragraph("PARÁMETROS DE CÁLCULO", self.subtitle_style))
        story.append(self._create_parameters_table(parameters))
        story.append(Spacer(1, 20))
        
        # Resultados del cálculo
        story.append(Paragraph("RESULTADOS DEL CÁLCULO", self.subtitle_style))
        story.append(self._create_results_table(calculation_result))
        
        # Estado de cumplimiento
        compliance_color = colors.green if calculation_result['compliance_status'] == 'APROBADO' else colors.red
        compliance_text = f"✅ APROBADO" if calculation_result['compliance_status'] == 'APROBADO' else "❌ RECHAZADO"
        
        result_style_with_color = ParagraphStyle(
            'ResultWithColor',
            parent=self.result_style,
            textColor=compliance_color
        )
        story.append(Paragraph(compliance_text, result_style_with_color))
        story.append(Spacer(1, 20))
        
        # Motivos de rechazo (si aplica)
        if calculation_result.get('rejection_reasons'):
            story.append(Paragraph("MOTIVOS DE RECHAZO", self.subtitle_style))
            for reason in calculation_result['rejection_reasons']:
                story.append(Paragraph(f"• {reason}", self.normal_style))
            story.append(Spacer(1, 20))
        
        # Recomendaciones
        if calculation_result.get('recommendations'):
            story.append(Paragraph("RECOMENDACIONES", self.subtitle_style))
            for rec in calculation_result['recommendations']:
                story.append(Paragraph(f"• {rec}", self.normal_style))
            story.append(Spacer(1, 20))
        
        # Información legal
        story.append(PageBreak())
        story.append(Paragraph("INFORMACIÓN LEGAL Y NORMATIVA", self.subtitle_style))
        story.append(self._create_legal_info())
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Reporte generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                               self.normal_style))
        story.append(Paragraph("Sistema Arquitect Assistant - Cálculo OGUC v1.0", 
                               self.normal_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_certificate_table(self, certificate_data: Dict[str, Any]) -> Table:
        """Crea tabla con datos del certificado"""
        data = [
            ['Campo', 'Valor'],
            ['Rol del Predio', certificate_data.get('rol', 'No especificado')],
            ['Dirección', certificate_data.get('direccion', 'No especificada')],
            ['Comuna', certificate_data.get('comuna', 'No especificada')],
            ['Superficie Terreno', f"{certificate_data.get('superficie_terreno', 0):.1f} m²"],
            ['Uso de Suelo', certificate_data.get('uso_suelo', 'No especificado')],
            ['Zona', certificate_data.get('zona', 'No especificada')],
            ['Propietario', certificate_data.get('nombre_propietario', 'No especificado')]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_parameters_table(self, parameters: Dict[str, Any]) -> Table:
        """Crea tabla con parámetros de cálculo"""
        data = [
            ['Parámetro', 'Valor'],
            ['Pisos Solicitados', str(parameters.get('floors', 0))],
            ['Tipo de Zona', parameters.get('zone_type', 'No especificado').title()],
            ['Superficie Mínima Vivienda', f"{parameters.get('min_dwelling_area', 40):.1f} m²"],
            ['Altura Máxima', f"{parameters.get('max_height', 0):.1f} m"],
            ['Coeficiente Constructibilidad', str(parameters.get('constructibility_coef', 0))],
            ['Porcentaje Ocupación', f"{parameters.get('occupation_percentage', 0):.1f}%"]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_results_table(self, calculation_result: Dict[str, Any]) -> Table:
        """Crea tabla con resultados del cálculo"""
        data = [
            ['Indicador', 'Resultado'],
            ['Superficie Total Terreno', f"{calculation_result.get('total_surface', 0):.1f} m²"],
            ['Cabida Máxima Edificación', f"{calculation_result.get('max_building_surface', 0):.1f} m²"],
            ['Superficie Máxima Emplazamiento', f"{calculation_result.get('max_occupation_surface', 0):.1f} m²"],
            ['Pisos Permitidos', str(calculation_result.get('allowed_floors', 0))],
            ['Altura Máxima Permitida', f"{calculation_result.get('max_height', 0):.1f} m"],
            ['Unidades Vivienda Máximas', str(calculation_result.get('dwelling_units_max', 0))],
            ['Utilización Coeficiente', f"{calculation_result.get('constructibility_utilization', 0):.1f}%"]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_legal_info(self) -> List[Paragraph]:
        """Crea sección de información legal"""
        legal_text = [
            "<b>Base Legal:</b>",
            "• Ordenanza General de Urbanismo y Construcciones (OGUC)",
            "• Decreto Supremo N° 47 de 1992, MINVU",
            "• Plan Regulador Comunal respectivo",
            "",
            "<b>Normativas Aplicadas:</b>",
            "• Artículo 2.6.3. del OGUC: Coeficiente de constructibilidad",
            "• Artículo 2.6.4. del OGUC: Superficie de emplazamiento",
            "• Artículo 2.6.5. del OGUC: Altura de edificación",
            "• Artículo 4.1.2. del OGUC: Superficie mínima de vivienda",
            "",
            "<b>Disposiciones Generales:</b>",
            "• Los cálculos se basan en la información proporcionada en el Certificado de Informaciones Previas",
            "• Se aplican las restricciones específicas según tipo de zona",
            "• Los resultados están sujetos a verificación municipal",
            "",
            "<b>Nota Importante:</b>",
            "Este informe es una herramienta de apoyo y no reemplaza la evaluación profesional ni la aprobación municipal. "
            "Se recomienda consultar con un arquitecto o ingeniero civil para la validación final del proyecto."
        ]
        
        paragraphs = []
        for text in legal_text:
            paragraphs.append(Paragraph(text, self.normal_style))
        
        return paragraphs
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> bytes:
        """Genera reporte resumen de múltiples cálculos"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        story.append(Paragraph("RESUMEN DE CÁLCULOS DE CABIDA", self.title_style))
        story.append(Spacer(1, 20))
        
        for i, result in enumerate(results, 1):
            story.append(Paragraph(f"CÁLCULO #{i}", self.subtitle_style))
            
            # Tabla resumen
            data = [
                ['Proyecto', result.get('project_name', f'Proyecto {i}')],
                ['Estado', result.get('compliance_status', 'Desconocido')],
                ['Cabida Máxima', f"{result.get('max_building_surface', 0):.1f} m²"],
                ['Unidades Máximas', str(result.get('dwelling_units_max', 0))]
            ]
            
            table = Table(data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 15))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
