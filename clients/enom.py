from typing import Optional
import requests
from urllib.parse import urlencode
import xmltodict
from core.config import settings


class EnomClient:
    """
    Client for interacting with the Enom API to register domains
    """

    def __init__(self, reseller_id, reseller_password, test_mode=True):
        """
        Initialize the Enom API client

        Args:
            reseller_id (str): Your Enom reseller ID
            reseller_password (str): Your Enom API password
            test_mode (bool): Whether to use the test environment (default: True)
        """
        self.reseller_id = reseller_id
        self.reseller_password = reseller_password

        if test_mode:
            self.base_url = "https://resellertest.enom.com/interface.asp"
        else:
            self.base_url = "https://reseller.enom.com/interface.asp"

    def check_domain_availability(self, domain_name):
        """
        Check if a domain is available for registration

        Args:
            domain_name (str): Domain name to check

        Returns:
            dict: Response from Enom API
        """
        sld, tld = domain_name.split(".")

        params = {
            "command": "Check",
            "SLD": sld,
            "TLD": tld,
            "UID": self.reseller_id,
            "PW": self.reseller_password,
            "ResponseType": "XML",
        }

        response = requests.get(f"{self.base_url}?{urlencode(params)}")
        return self._parse_response(response.text)

    def _register_domain(
        self, domain_name: str, contact_info: dict, registration_period: int = 1
    ) -> dict:
        """
        Register a new domain

        Args:
            domain_name (str): Domain name to register
            registration_period (int): Number of years to register (default: 1)
            contact_info (dict): Contact information for the domain

        Returns:
            dict: Response from Enom API
        """
        if not contact_info:
            raise ValueError("Contact information is required for domain registration")

        sld, tld = domain_name.split(".")

        params = {
            "command": "Purchase",
            "SLD": sld,
            "TLD": tld,
            "UID": self.reseller_id,
            "PW": self.reseller_password,
            "NumYears": registration_period,
            "ResponseType": "XML",
        }

        contact_fields = {
            "RegistrantFirstName": contact_info.get("first_name", ""),
            "RegistrantLastName": contact_info.get("last_name", ""),
            "RegistrantOrganizationName": contact_info.get("organization", ""),
            "RegistrantAddress1": contact_info.get("address1", ""),
            "RegistrantAddress2": contact_info.get("address2", ""),
            "RegistrantCity": contact_info.get("city", ""),
            "RegistrantStateProvince": contact_info.get("state", ""),
            "RegistrantPostalCode": contact_info.get("postal_code", ""),
            "RegistrantCountry": contact_info.get("country", ""),
            "RegistrantPhone": contact_info.get("phone", ""),
            "RegistrantEmailAddress": contact_info.get("email", ""),
        }
        params.update(contact_fields)

        response = requests.get(f"{self.base_url}?{urlencode(params)}")
        return self._parse_xml_response(response)

    def register_domain_with_valid_response(
        self, domain_name: str, contact_info: dict, registration_period: int = 1
    ) -> dict:
        result = {"result": "", "additional": ""}

        registered = self._register_domain(
            domain_name=domain_name,
            contact_info=contact_info,
            registration_period=registration_period,
        )
        interface_response = registered.get("interface-response")
        if not interface_response:
            result["result"] = "Not registered"
            result["additional"] = "Failed to get interface response"
            return result

        rrp_code = interface_response.get("RRPCode")

        if not rrp_code:
            result["result"] = "Not registered"
            result["additional"] = "Failed to get RRP Code"
            return result

        if rrp_code != "200":
            result["result"] = "Not registered"
            result["additional"] = (
                f"{interface_response.get('RRPText', 'Failed to get RRPText')}, error_count: {interface_response.get('ErrCount')}, errors: {interface_response.get('errors')}"
            )
            return result

        result["result"] = interface_response.get(
            "OrderStatus", "Failed to get OrderStatus"
        )
        result["additional"] = interface_response.get(
            "OrderDescription", "Failed to get OrderDescription"
        )

        return result

    def _parse_xml_response(self, response: requests.Response) -> dict:
        """
        Basic response parsing - in a production environment,
        you would want to properly parse the XML response

        For simplicity, this is just returning the raw response
        """
        xml_str = response.content.decode("utf-8")

        data_dict = xmltodict.parse(xml_str)
        return data_dict

    def check_domain_availability(self, domain_name):
        """
        Check if a domain is available for registration

        Args:
            domain_name (str): Domain name to check

        Returns:
            bool: True if domain is available, False otherwise
        """
        sld, tld = domain_name.split(".")
        params = {
            "command": "Check",
            "SLD": sld,
            "TLD": tld,
            "UID": self.reseller_id,
            "PW": self.reseller_password,
            "ResponseType": "XML",
        }

        response = requests.get(f"{self.base_url}?{urlencode(params)}")
        # In production, parse XML properly
        return "Domain is available" in response.text

    def register_domain_for_account(
        self,
        domain_name,
        registration_period=1,
        contact_info=None,
        reseller_id: Optional[str] = None,
        reseller_password: Optional[str] = None,
    ):
        """
        Register a new domain for a specific account

        Args:
            account_id (str): Enom account ID to register the domain under
            domain_name (str): Domain name to register
            registration_period (int): Number of years to register (default: 1)
            contact_info (dict): Contact information for the domain
            name_servers (list): List of name servers

        Returns:
            dict: Response information including success status and order ID
        """
        if contact_info is None:
            raise ValueError("Contact information is required for domain registration")

        # Extract SLD (second-level domain) and TLD (top-level domain)
        sld, tld = domain_name.split(".")

        uid = reseller_id if reseller_id else self.reseller_id
        pw = reseller_password if reseller_password else self.reseller_password

        # Base parameters
        params = {
            "command": "Purchase",
            "SLD": sld,
            "TLD": tld,
            "UID": uid,
            "PW": pw,
            "NumYears": registration_period,
            "ResponseType": "XML",
            # "EndUserID": account_id,  # This is the key parameter that assigns the domain to the account
        }

        # Add required contact information
        required_fields = {
            "RegistrantFirstName": contact_info.get("first_name", ""),
            "RegistrantLastName": contact_info.get("last_name", ""),
            "RegistrantAddress1": contact_info.get("address1", ""),
            "RegistrantCity": contact_info.get("city", ""),
            "RegistrantPostalCode": contact_info.get("postal_code", ""),
            "RegistrantCountry": contact_info.get("country", ""),
            "RegistrantPhone": contact_info.get("phone", ""),
            "RegistrantEmailAddress": contact_info.get("email", ""),
        }

        # Add optional fields if provided
        optional_fields = {}
        if "organization" in contact_info and contact_info["organization"]:
            optional_fields["RegistrantOrganizationName"] = contact_info["organization"]
        if "address2" in contact_info and contact_info["address2"]:
            optional_fields["RegistrantAddress2"] = contact_info["address2"]
        if "state" in contact_info and contact_info["state"]:
            optional_fields["RegistrantStateProvince"] = contact_info["state"]

        params.update(required_fields)
        params.update(optional_fields)

        # Add name servers if provided
        # if name_servers:
        #     for i, ns in enumerate(name_servers, 1):
        #         params[f"NS{i}"] = ns

        response = requests.get(f"{self.base_url}?{urlencode(params)}")

        xml_str = response.content.decode("utf-8")

        data_dict = xmltodict.parse(xml_str)

        # In production, parse XML properly
        # This is a simplified response parsing
        success = "OrderID" in response.text

        # Extract OrderID (in production, use proper XML parsing)
        order_id = None
        if success:
            # Simplified extraction - in production use proper XML parsing
            import re

            order_id_match = re.search(r"<OrderID>(\d+)</OrderID>", response.text)
            if order_id_match:
                order_id = order_id_match.group(1)

        return {"success": success, "order_id": order_id, "raw_response": response.text}

    def get_domains_by_account(self, account_id):
        """
        Get all domains for a specific account

        Args:
            account_id (str): Enom account ID

        Returns:
            list: List of domain dictionaries
        """
        params = {
            "command": "GetDomains",
            "UID": self.reseller_id,
            "PW": self.reseller_password,
            # "AccountID": account_id,
            "Tab": "Sub_IOwn",
            "ResponseType": "XML",
        }

        response = requests.get(f"{self.base_url}?{urlencode(params)}")

        xml_str = response.content.decode("utf-8")

        data_dict = xmltodict.parse(xml_str)

        # In production, properly parse the XML to extract domain information
        # This is a simplified example
        domains = []

        # Simple regex-based parsing (use proper XML parsing in production)
        import re

        domain_matches = re.findall(r"<domain>([^<]+)</domain>", response.text)
        expiration_matches = re.findall(
            r"<expiration>([^<]+)</expiration>", response.text
        )

        # Combine the matches into domain objects
        for i in range(len(domain_matches)):
            domain_name = domain_matches[i] if i < len(domain_matches) else None
            expiration = expiration_matches[i] if i < len(expiration_matches) else None

            if domain_name:
                domains.append({"domain_name": domain_name, "expiration": expiration})

        return domains

    def create_sub_account(
        self, username, password, email, first_name=None, last_name=None
    ):
        """
        Create a new account under your reseller account

        Args:
            username (str): Account username
            password (str): Account password
            email (str): Account email address
            first_name (str): First name
            last_name (str): Last name

        Returns:
            bool: Success status
        """
        params = {
            "command": "CreateSubAccount",
            "uid": self.reseller_id,
            "pw": self.reseller_password,
            "NewUID": username,
            "NewPW": password,
            "ConfirmPW": password,
            "RegistrantEmailAddress": email,
            # "RegistrantOrganizationName": "Test Org",
            # "RegistrantFirstName": first_name or "John",
            # "RegistrantLastName": last_name or "Doe",
            # "RegistrantAddress1": "123 Main Street",
            # "RegistrantCity": "New York",
            # "RegistrantCountry": "US",
            # "RegistrantPostalCode": "10001",
            "RegistrantPhone": "+1.1234567890",
            # "AuthQuestionType": "Pet's name",
            # "AuthQuestionAnswer": "Fluffy",
            "ResponseType": "XML",
        }

        response = requests.get(f"{self.base_url}?{urlencode(params)}")
        xml_str = response.content.decode("utf-8")

        data_dict = xmltodict.parse(xml_str)
        return "successfully" in response.text.lower()

    def get_sub_accounts(self):
        """
        Create a new account under your reseller account

        Args:
            username (str): Account username
            password (str): Account password
            email (str): Account email address
            first_name (str): First name
            last_name (str): Last name

        Returns:
            bool: Success status
        """
        params = {
            "command": "GetSubAccounts",
            "uid": self.reseller_id,
            "pw": self.reseller_password,
            "ResponseType": "XML",
        }

        response = requests.get(f"{self.base_url}?{urlencode(params)}")
        xml_str = response.content.decode("utf-8")

        data_dict = xmltodict.parse(xml_str)
        return "successfully" in response.text.lower()


enom_client = None


def get_enom_client() -> EnomClient:
    """Dependency provider for the EnomClient."""
    global enom_client
    if enom_client is None:
        enom_client = EnomClient(
            reseller_id=settings.ENOM_RESELLER_ID,
            reseller_password=settings.ENOM_RESELLER_PASSWORD,
            test_mode=settings.ENOM_TEST_MODE,
        )
    return enom_client
