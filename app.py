from random import choice, randint
from fastapi import FastAPI

app = FastAPI()

@app.get("/check-domain")
async def check_domains(domain: str):
    is_free = choice([True, False])
    price = randint(1, 100)
    return {"domain": domain, "is_free": is_free, "price": price}
