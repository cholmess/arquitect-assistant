# Arquitect Assistant - Sistema de Cálculo de Cabidas OGUC

Sistema automatizado para procesar Certificados de Informaciones Previas chilenos y calcular cabidas según normativa OGUC.

## 🚀 Características

- **Procesamiento automático** de Certificados de Informaciones Previas (PDF/imagen)
- **Cálculo de cabidas** según normativa OGUC actualizada
- **Validación normativa** con aprobación/rechazo automático
- **OCR integrado** para documentos no estructurados
- **API REST** para integración con sistemas existentes
- **Reportes detallados** con recomendaciones

## 📋 Requisitos

- Python 3.9+
- Tesseract OCR (para procesamiento de imágenes)
- 2GB RAM mínimo
- 1GB espacio en disco

## 🛠️ Instalación

### Backend

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd arquitect-assistant/backend
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Instalar Tesseract OCR:
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Descargar desde https://github.com/UB-Mannheim/tesseract/wiki
```

## 🏃‍♂️ Ejecución

### Iniciar servidor backend:
```bash
cd backend
python main.py
```

El servidor estará disponible en `http://localhost:8000`

### Documentación API:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📊 Uso de la API

### 1. Subir Certificado
```bash
curl -X POST "http://localhost:8000/api/v1/upload/certificate" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@certificado.pdf" \
  -F "floors=3" \
  -F "zone_type=residencial" \
  -F "min_dwelling_area=40.0"
```

### 2. Calcular Cabida
```bash
curl -X POST "http://localhost:8000/api/v1/calculate/cabida" \
  -H "Content-Type: application/json" \
  -d '{
    "certificate_data": {
      "superficie_terreno": 500,
      "coeficiente_constructibilidad": 1.2,
      "porcentaje_ocupacion": 60
    },
    "floors": 3,
    "zone_type": "residencial"
  }'
```

### 3. Validar Cumplimiento
```bash
curl -X POST "http://localhost:8000/api/v1/validate/compliance" \
  -H "Content-Type: application/json" \
  -d '{
    "certificate_data": {...},
    "floors": 3,
    "zone_type": "residencial"
  }'
```

## 🏗️ Arquitectura

```
backend/
├── app/
│   ├── api/              # Endpoints REST
│   │   ├── upload.py     # Subida de archivos
│   │   ├── calculate.py  # Cálculo de cabidas
│   │   └── validate.py   # Validación normativa
│   ├── core/             # Lógica de negocio
│   │   ├── oguc_calculator.py  # Motor OGUC
│   │   ├── pdf_processor.py    # Procesamiento PDF/OCR
│   │   └── config.py           # Configuración
│   └── models/           # Modelos de datos
│       └── certificate.py
├── main.py               # Aplicación FastAPI
└── requirements.txt      # Dependencias
```

## 📋 Normativas OGUC Implementadas

### Validaciones Principales
- ✅ Superficie mínima de terreno (40m² para vivienda)
- ✅ Coeficiente de constructibilidad (0.5 - 3.0 según zona)
- ✅ Altura máxima de edificación
- ✅ Porcentaje de ocupación de suelo
- ✅ Uso de suelo permitido

### Tipos de Zona Soportados
- **Residencial**: Altura máx 23m, Coef. máx 2.0, Ocupación 60%
- **Comercial**: Altura máx 30m, Coef. máx 3.0, Ocupación 80%
- **Industrial**: Altura máx 25m, Coef. máx 2.5, Ocupación 70%
- **Mixto**: Altura máx 28m, Coef. máx 2.5, Ocupación 70%

## 🧪 Testing

Ejecutar tests:
```bash
cd backend
pytest tests/ -v
```

Cobertura de tests:
```bash
pytest --cov=app tests/
```

## 📝 Ejemplo de Respuesta

### Cálculo Aprobado
```json
{
  "success": true,
  "result": {
    "compliance_status": "APROBADO",
    "max_building_surface": 600.0,
    "dwelling_units_max": 15,
    "allowed_floors": 3,
    "rejection_reasons": [],
    "recommendations": [
      "✅ El proyecto cumple con las normativas OGUC básicas",
      "📊 Cabida máxima permitida: 600.0m²"
    ]
  }
}
```

### Cálculo Rechazado
```json
{
  "success": true,
  "result": {
    "compliance_status": "RECHAZADO",
    "rejection_reasons": [
      "Superficie del terreno (35m²) inferior al mínimo legal (40m²)"
    ],
    "recommendations": [
      "❌ El proyecto no cumple con las normativas OGUC",
      "📋 Revise los motivos de rechazo indicados"
    ]
  }
}
```

## 🔧 Configuración

Variables de entorno principales:

```bash
# Límites de archivo
MAX_FILE_SIZE=10485760          # 10MB
ALLOWED_EXTENSIONS=.pdf,.jpg,.jpeg,.png

# Configuración OGUC
MIN_SURFACE_AREA=40.0           # m² mínimos
DEFAULT_MAX_HEIGHT=23.0         # metros
DEFAULT_CONSTRUCTIBILITY_COEF=1.0

# Base de datos
DATABASE_URL=sqlite:///./arquitect_assistant.db
```

## 🚀 Despliegue

### Docker
```bash
docker build -t arquitect-assistant .
docker run -p 8000:8000 arquitect-assistant
```

### Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE

## 📞 Soporte

- 📧 Email: soporte@arquitect-assistant.cl
- 📖 Documentación: docs.arquitect-assistant.cl
- 🐛 Issues: GitHub Issues

---

**Desarrollado con ❤️ para arquitectos chilenos**
