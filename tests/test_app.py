from unittest.mock import MagicMock, patch
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

def test_purchase_domain_success():
    """
    Test successful domain purchase
    """
    request_data = {
        "domain_name": "example.com",
        "contact_info": {
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "address1": "123 Main St",
            "city": "Anytown",
            "postal_code": "12345",
            "country": "US",
            
            "first_name": "John",
            "organization": "Test Corp",
            "address2": "Suite 100",
            "state": "CA",
            "phone_country_code": "+1",
            "phone": "1234567890"
        }
    }

    mock_enom_client = MagicMock()
    mock_enom_client.register_domain_with_valid_response.return_value = {
        "result": "Registered",
        "additional": "Domain successfully registered"
    }

    with patch("app.enom_client", mock_enom_client):
        response = client.post("/domains/purchase", json=request_data)

        print("Success Test Response:", response.status_code, response.json())

        assert response.status_code == 200
        assert response.json() == {
            "result": "Registered",
            "additional": "Domain successfully registered"
        }


def test_purchase_domain_registration_failure():
    """
    Test domain purchase with registration failure
    """
    request_data = {
        "domain_name": "example.com",
        "contact_info": {
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "address1": "123 Main St",
            "city": "Anytown",
            "postal_code": "12345",
            "country": "US",
            
            "first_name": "John",
            "organization": "Test Corp",
            "address2": "Suite 100",
            "state": "CA",
            "phone_country_code": "+1",
            "phone": "1234567890"
        }
    }

    mock_enom_client = MagicMock()
    mock_enom_client.register_domain_with_valid_response.return_value = {
        "result": "Not registered",
        "additional": "Domain registration failed: Insufficient funds"
    }

    with patch("app.enom_client", mock_enom_client):
        response = client.post("/domains/purchase", json=request_data)

        print("Failure Test Response:", response.status_code, response.json())

        assert response.status_code == 200
        assert response.json() == {
            "result": "Not registered",
            "additional": "Domain registration failed: Insufficient funds"
        }


def test_purchase_domain_exception():
    """
    Test domain purchase when an unexpected exception occurs
    """
    request_data = {
        "domain_name": "example.com",
        "contact_info": {
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "address1": "123 Main St",
            "city": "Anytown",
            "postal_code": "12345",
            "country": "US",
            
            "first_name": "John",
            "organization": "Test Corp",
            "address2": "Suite 100",
            "state": "CA",
            "phone_country_code": "+1",
            "phone": "1234567890"
        }
    }

    mock_enom_client = MagicMock()
    mock_enom_client.register_domain_with_valid_response.side_effect = Exception("Unexpected error occurred")

    with patch("app.enom_client", mock_enom_client):
        response = client.post("/domains/purchase", json=request_data)

        print("Exception Test Response:", response.status_code, response.json())

        assert response.status_code == 500
        assert response.json() == {"detail": "Unexpected error occurred"}


def test_purchase_domain_missing_required_fields():
    """
    Test domain purchase with missing required contact information
    """
    request_data = {
        "domain_name": "example.com",
        "contact_info": {
            "first_name": "John"
        }
    }

    response = client.post("/domains/purchase", json=request_data)

    print("Missing Fields Test Response:", response.status_code, response.json())

    assert response.status_code == 422
    assert "detail" in response.json()
