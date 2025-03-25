from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_generate_domains():
    mock_domains = [
        {"name": "example.com", "price": 10.0},
        {"name": "test.com", "price": 20.0},
    ]

    request_data = {
        "name": "example",
        "description": "test description",
        "keywords": "test",
        "count": 2,
    }

    with patch("app.generate_domains_func") as mock_generate:
        mock_generate.return_value = mock_domains

        response = client.post("/domains/generate", json=request_data)

        assert response.status_code == 200
        assert response.json() == mock_domains

        mock_generate.assert_called_once_with(
            name="example", description="test description", keywords="test", count=2
        )


def test_generate_domains_error():
    request_data = {
        "name": "example",
        "description": "test description",
        "keywords": "test",
        "count": 2,
    }

    with patch("app.generate_domains_func") as mock_generate:
        mock_generate.side_effect = Exception("Test error")

        response = client.post("/domains/generate", json=request_data)

        assert response.status_code == 500
        assert response.json() == {"detail": "Test error"}
