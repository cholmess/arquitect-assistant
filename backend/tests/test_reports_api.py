import httpx
import pytest
import pytest_asyncio

from main import app


@pytest_asyncio.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def _sample_report_payload():
    return {
        "certificate_data": {
            "rol": "123-45",
            "comuna": "Santiago",
            "superficie_terreno": 500.0,
            "direccion": "Calle Falsa 123",
            "nombre_propietario": "Juan Perez",
            "uso_suelo": "Residencial",
            "zona": "Z1",
            "altura_maxima": 23.0,
            "coeficiente_constructibilidad": 1.2,
            "porcentaje_ocupacion": 60.0,
        },
        "calculation_result": {
            "total_surface": 500.0,
            "max_building_surface": 600.0,
            "max_occupation_surface": 300.0,
            "allowed_floors": 3,
            "max_height": 23.0,
            "constructibility_utilization": 100.0,
            "dwelling_units_max": 15,
            "compliance_status": "APROBADO",
            "rejection_reasons": [],
            "recommendations": ["OK"],
        },
        "parameters": {
            "floors": 3,
            "zone_type": "residencial",
            "min_dwelling_area": 40.0,
        },
    }


@pytest.mark.asyncio
async def test_preview_report_returns_success(async_client):
    response = await async_client.post(
        "/api/v1/reports/preview-report",
        json=_sample_report_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["report_ready"] is True
    assert payload["preview"]["calculation_summary"]["compliance_status"] == "APROBADO"


@pytest.mark.asyncio
async def test_generate_pdf_returns_pdf_response(async_client):
    response = await async_client.post(
        "/api/v1/reports/generate-pdf",
        json=_sample_report_payload(),
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
