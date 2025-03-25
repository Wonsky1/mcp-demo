import pytest
import requests
from unittest.mock import patch, MagicMock
import xmltodict

from clients.enom import EnomClient


@pytest.fixture
def mock_enom_client():
    """Fixture to create an EnomClient instance for testing"""
    return EnomClient(
        reseller_id="test_reseller", reseller_password="test_password", test_mode=True
    )


def test_enom_client_initialization(mock_enom_client):
    """Test the initialization of the EnomClient"""
    assert mock_enom_client.reseller_id == "test_reseller"
    assert mock_enom_client.reseller_password == "test_password"
    assert mock_enom_client.base_url == "https://resellertest.enom.com/interface.asp"


@patch("requests.post")
def test_check_domain_availability_available(mock_get, mock_enom_client):
    """Test domain availability check for an available domain"""
    mock_response = MagicMock()
    mock_response.text = "Domain is available"
    mock_get.return_value = mock_response

    result = mock_enom_client.check_domain_availability("example.com")

    assert result is True
    mock_get.assert_called_once()


@patch("requests.post")
def test_check_domain_availability_unavailable(mock_get, mock_enom_client):
    """Test domain availability check for an unavailable domain"""
    mock_response = MagicMock()
    mock_response.text = "Domain is not available"
    mock_get.return_value = mock_response

    result = mock_enom_client.check_domain_availability("example.com")

    assert result is False
    mock_get.assert_called_once()


@patch("requests.post")
def test_register_domain_for_account_success(mock_get, mock_enom_client):
    """Test successful domain registration"""
    mock_response = MagicMock()
    mock_response.text = "<OrderID>12345</OrderID>"
    mock_response.content = b"<response><OrderID>12345</OrderID></response>"
    mock_get.return_value = mock_response

    contact_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "address1": "123 Main St",
        "city": "Anytown",
        "postal_code": "12345",
        "country": "US",
        "phone": "+1.1234567890",
    }

    result = mock_enom_client.register_domain_for_account(
        domain_name="example.com", contact_info=contact_info
    )

    assert result["success"] is True
    assert result["order_id"] == "12345"
    mock_get.assert_called_once()


def test_register_domain_for_account_no_contact_info(mock_enom_client):
    """Test domain registration fails without contact info"""
    with pytest.raises(ValueError, match="Contact information is required"):
        mock_enom_client.register_domain_for_account("example.com")


@patch("requests.post")
def test_create_sub_account_success(mock_get, mock_enom_client):
    """Test successful sub-account creation"""
    mock_response = MagicMock()
    mock_response.text = "Account created successfully"
    mock_response.content = b"<response>Account created successfully</response>"
    mock_get.return_value = mock_response

    result = mock_enom_client.create_sub_account(
        username="testuser", password="testpass", email="test@example.com"
    )

    assert result is True
    mock_get.assert_called_once()


@patch("requests.post")
def test_get_domains_by_account(mock_get, mock_enom_client):
    """Test retrieving domains for an account"""
    mock_response = MagicMock()
    mock_response.text = """
    <response>
        <domain>example1.com</domain>
        <expiration>2024-12-31</expiration>
        <domain>example2.com</domain>
        <expiration>2025-01-15</expiration>
    </response>
    """
    mock_response.content = mock_response.text.encode("utf-8")
    mock_get.return_value = mock_response

    domains = mock_enom_client.get_domains_by_account("account123")

    assert len(domains) == 2
    assert domains[0]["domain_name"] == "example1.com"
    assert domains[0]["expiration"] == "2024-12-31"
    assert domains[1]["domain_name"] == "example2.com"
    assert domains[1]["expiration"] == "2025-01-15"
    mock_get.assert_called_once()


@patch("requests.post")
def test_register_domain_with_valid_response_success(mock_get, mock_enom_client):
    """Test successful domain registration with valid response"""
    mock_response = MagicMock()
    mock_response.content = b"""
    <interface-response>
        <RRPCode>200</RRPCode>
        <OrderStatus>Completed</OrderStatus>
        <OrderDescription>Domain registered successfully</OrderDescription>
    </interface-response>
    """
    mock_get.return_value = mock_response

    contact_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "address1": "123 Main St",
        "city": "Anytown",
        "postal_code": "12345",
        "country": "US",
        "phone": "+1.1234567890",
    }

    result = mock_enom_client.register_domain_with_valid_response(
        domain_name="example.com", contact_info=contact_info
    )

    assert result["result"] == "Completed"
    assert result["additional"] == "Domain registered successfully"
    mock_get.assert_called_once()


@patch("requests.post")
def test_register_domain_with_valid_response_failure(mock_get, mock_enom_client):
    """Test domain registration with invalid RRP code"""
    mock_response = MagicMock()
    mock_response.content = b"""
    <interface-response>
        <RRPCode>400</RRPCode>
        <RRPText>Domain registration failed</RRPText>
        <ErrCount>1</ErrCount>
        <errors>Invalid contact information</errors>
    </interface-response>
    """
    mock_get.return_value = mock_response

    contact_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "address1": "123 Main St",
        "city": "Anytown",
        "postal_code": "12345",
        "country": "US",
        "phone": "+1.1234567890",
    }

    result = mock_enom_client.register_domain_with_valid_response(
        domain_name="example.com", contact_info=contact_info
    )

    assert result["result"] == "Not registered"
    assert "Domain registration failed" in result["additional"]
    mock_get.assert_called_once()
