import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class DomainsGenerationRequest(BaseModel):
    name: str
    description: str = ""
    keywords: str = ""
    count: int


class GeneratedDomain(BaseModel):
    name: str
    price: float


class ContactInfo(BaseModel):
    # Required fields
    last_name: str
    address1: str
    city: str
    postal_code: str
    country: str
    email: EmailStr

    # Optional fields with default empty string
    first_name: str = ""
    organization: str = ""
    address2: str = ""
    state: str = ""
    phone_country_code: str = ""
    phone: str = ""

    @field_validator('phone')
    def validate_phone(cls, v, values):
        if v:
            # Remove any spaces, dashes, or parentheses
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', v)
            
            # Check if phone contains only digits
            if not cleaned_phone.isdigit():
                raise ValueError('Phone number must contain only digits, spaces, dashes, or parentheses')
            
            # Check length (assuming standard phone number length between 8 and 15 digits)
            if not (8 <= len(cleaned_phone) <= 15):
                raise ValueError('Phone number must be between 8 and 15 digits')
            
            return cleaned_phone
        return v

    @field_validator('phone_country_code')
    def validate_country_code(cls, v):
        if v:
            # Remove any spaces and plus sign
            cleaned_code = v.replace(' ', '').replace('+', '')
            
            # Check if country code contains only digits
            if not cleaned_code.isdigit():
                raise ValueError('Country code must contain only digits')
            
            # Check length (country codes are typically 1-3 digits)
            if not (1 <= len(cleaned_code) <= 3):
                raise ValueError('Country code must be between 1 and 3 digits')
            
            return f"+{cleaned_code}"  # Always return with plus prefix
        return v

    @field_validator('country')
    def validate_country(cls, v):
        cleaned_country = v.strip().upper()
        
        if not re.match(r'^[A-Z]{2}$', cleaned_country):
            raise ValueError('Country must be a valid 2-letter ISO country code')
        
        return cleaned_country

class RegisterDomainRequest(BaseModel):
    domain_name: str = Field(..., description="Domain name to register")
    contact_info: ContactInfo
    
    @field_validator('domain_name')
    def validate_domain_name(cls, v):
        pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
        
        if not re.match(pattern, v, re.IGNORECASE):
            raise ValueError("Invalid domain name format. Please provide a valid domain name (e.g., example.com)")
        
        # Check length constraints
        if len(v) < 3:
            raise ValueError("Domain name is too short")
        if len(v) > 253:
            raise ValueError("Domain name is too long (maximum 253 characters)")
        
        # Check if domain has at least one dot and valid TLD
        parts = v.split('.')
        if len(parts) < 2:
            raise ValueError("Domain must include at least one dot and a valid TLD")
        
        return v