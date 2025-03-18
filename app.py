from random import choice, randint
from typing import List
from fastapi import FastAPI, HTTPException
from tools.utils import generate_domains as generate_domains_func

from schemas.models import DomainsGenerationRequest, GeneratedDomain

app = FastAPI()


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
