from pydantic import BaseModel


class DomainsGenerationRequest(BaseModel):
    name: str
    description: str = ""
    keywords: str = ""
    count: int


class GeneratedDomain(BaseModel):
    name: str
    price: float


# class DomainsGenerationResponse(BaseModel):
