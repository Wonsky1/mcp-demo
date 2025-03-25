from random import choice, randint
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from clients.enom import EnomClient, get_enom_client
from tools.utils import generate_domains as generate_domains_func

from schemas.models import ContactInfo, DomainsGenerationRequest, GeneratedDomain, RegisterDomainRequest

enom_client: EnomClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global enom_client
    enom_client = get_enom_client()

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/check-domain")
async def check_domains(domain: str):
    is_available = choice([True, False])
    price = randint(1, 100)
    return {"domain": domain, "is_available": is_available, "price": price}


@app.post("/domains/generate", response_model=list[GeneratedDomain])
async def generate_domains(request: DomainsGenerationRequest):
    try:
        domains = generate_domains_func(
            name=request.name,
            description=request.description,
            keywords=request.keywords,
            count=request.count,
        )

        return domains
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/domains/purchase")
async def purchase_domain(request: RegisterDomainRequest):
    try:
        domain_name = request.domain_name
        contact_info = request.contact_info.model_dump()
        result = enom_client.register_domain_with_valid_response(
            domain_name=domain_name,
            contact_info=contact_info
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
