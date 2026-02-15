import pytest
import httpx
import pytest_asyncio

from main import app


@pytest_asyncio.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_calculate_returns_400_when_surface_missing(async_client):
    response = await async_client.post(
        "/api/v1/calculate/cabida",
        json={
            "certificate_data": {},
            "floors": 3,
            "zone_type": "residencial",
            "min_dwelling_area": 40.0,
        },
    )

    assert response.status_code == 400
    assert "superficie del terreno" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_calculate_optimization_recommendation_uses_requested_floors(async_client):
    response = await async_client.post(
        "/api/v1/calculate/cabida",
        json={
            "certificate_data": {
                "superficie_terreno": 500.0,
                "altura_maxima": 7.0,
                "coeficiente_constructibilidad": 1.0,
                "porcentaje_ocupacion": 60.0,
            },
            "floors": 5,
            "zone_type": "residencial",
            "min_dwelling_area": 40.0,
        },
    )

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert any("en lugar de los 5 solicitados" in item for item in recommendations)


@pytest.mark.asyncio
async def test_validate_compliance_returns_200_with_default_constructibility_warning(async_client):
    response = await async_client.post(
        "/api/v1/validate/compliance",
        json={
            "certificate_data": {
                "superficie_terreno": 500.0,
                "rol": "123-45",
                "comuna": "Santiago",
                "altura_maxima": 23.0,
                "porcentaje_ocupacion": 60.0,
            },
            "floors": 3,
            "zone_type": "residencial",
            "min_dwelling_area": 40.0,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "warnings" in payload
    assert any(
        item["field"] == "constructibility" and item["severity"] == "info"
        for item in payload["warnings"]
    )


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_extension_with_400(async_client):
    response = await async_client.post(
        "/api/v1/upload/certificate",
        files={"file": ("archivo.txt", b"contenido", "text/plain")},
        data={
            "floors": "3",
            "zone_type": "residencial",
            "min_dwelling_area": "40.0",
        },
    )

    assert response.status_code == 400
    assert "formato de archivo no permitido" in response.json()["detail"].lower()
