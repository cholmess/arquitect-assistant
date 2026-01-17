import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
from typing import Dict, Optional, List
from pydantic import BaseModel

class CertificateData(BaseModel):
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

class PDFProcessor:
    def __init__(self):
        # Patrones regex para extraer datos del certificado
        self.patterns = {
            'rol': r'Rol:\s*(\d+-\d+)',
            'superficie': r'Superficie\s*(?:terreno|del terreno):\s*([\d.,]+)\s*m[²2]',
            'direccion': r'Dirección:\s*([^\n]+)',
            'comuna': r'Comuna:\s*([^\n]+)',
            'propietario': r'Propietario:\s*([^\n]+)',
            'uso_suelo': r'Uso\s*de\s*suelo:\s*([^\n]+)',
            'zona': r'Zona:\s*([^\n]+)',
            'altura': r'Altura\s*máxima:\s*([\d.,]+)\s*m',
            'constructibilidad': r'Coeficiente\s*de\s*constructibilidad:\s*([\d.,]+)',
            'ocupacion': r'Porcentaje\s*de\s*ocupación:\s*([\d.,]+)%'
        }
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extrae todo el texto de un PDF"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise ValueError(f"Error procesando PDF: {str(e)}")
    
    def extract_text_from_image(self, image_content: bytes) -> str:
        """Extrae texto de una imagen usando OCR"""
        try:
            image = Image.open(io.BytesIO(image_content))
            text = pytesseract.image_to_string(image, lang='spa')
            return text
        except Exception as e:
            raise ValueError(f"Error procesando imagen con OCR: {str(e)}")
    
    def extract_certificate_data(self, text: str) -> CertificateData:
        """Extrae datos estructurados del texto del certificado"""
        data = CertificateData(raw_text=text)
        
        for field, pattern in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Limpiar y convertir valores numéricos
                if field in ['superficie', 'altura', 'constructibilidad', 'ocupacion']:
                    value = value.replace(',', '.')
                    try:
                        numeric_value = float(value)
                        setattr(data, field, numeric_value)
                    except ValueError:
                        continue
                else:
                    setattr(data, field, value)
        
        return data
    
    def validate_certificate_format(self, text: str) -> bool:
        """Valida si el texto corresponde a un Certificado de Informaciones Previas"""
        required_keywords = [
            'certificado de informaciones previas',
            'municipalidad',
            'rol',
            'superficie'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in required_keywords)
    
    def process_file(self, file_content: bytes, filename: str) -> CertificateData:
        """Procesa un archivo (PDF o imagen) y extrae datos del certificado"""
        
        # Determinar tipo de archivo
        if filename.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            text = self.extract_text_from_image(file_content)
        else:
            raise ValueError("Formato de archivo no soportado")
        
        # Validar que sea un certificado válido
        if not self.validate_certificate_format(text):
            raise ValueError("El documento no parece ser un Certificado de Informaciones Previas válido")
        
        # Extraer datos estructurados
        certificate_data = self.extract_certificate_data(text)
        
        return certificate_data
    
    def extract_additional_data(self, text: str) -> Dict:
        """Extrae datos adicionales que puedan ser útiles"""
        additional_data = {}
        
        # Buscar coordenadas o referencias geográficas
        coord_pattern = r'(\d+°\d+\'\d+[NS])\s*(\d+°\d+\'\d+[WE])'
        coord_match = re.search(coord_pattern, text)
        if coord_match:
            additional_data['coordinates'] = f"{coord_match.group(1)} {coord_match.group(2)}"
        
        # Buscar fecha del certificado
        date_pattern = r'(\d{1,2})\s*de\s*(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s*de\s*(\d{4})'
        date_match = re.search(date_pattern, text, re.IGNORECASE)
        if date_match:
            additional_data['certificate_date'] = f"{date_match.group(1)} {date_match.group(2)} {date_match.group(3)}"
        
        # Buscar número de certificado
        cert_number_pattern = r'N[°o]\s*(\d+/\d{4})'
        cert_match = re.search(cert_number_pattern, text)
        if cert_match:
            additional_data['certificate_number'] = cert_match.group(1)
        
        return additional_data
