from random import choice, randint
from fastapi import FastAPI

app = FastAPI()

@app.get("/check-domain")
async def check_domains(domain: str):
    is_available = choice([True, False])
    price = randint(1, 100)
    return {"domain": domain, "is_available": is_available, "price": price}
