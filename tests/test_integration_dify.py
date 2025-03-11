import re
from unittest.mock import patch
import requests
from dotenv import load_dotenv
import os

load_dotenv()

DIFY_API_KEY = os.getenv("DIFY_API_KEY")

def generate_domains(name: str, description: str = "", keywords: list = [], count: int = 15) -> list:
    url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": {
            "name": name,
            "description": description,
            "keywords": keywords,
            "count": count
        },
        "response_mode": "blocking",
        "user": "test-user"
    }
    response = requests.post(url, headers=headers, json=data)
    json_response = response.json()
    return json_response["data"]["outputs"]["output"]


def test_domain_list_structure():
    domains = generate_domains("destilabs", "an outsource company", ["AI"])
    
    # Test that we get the expected number of domains
    assert len(domains) == 15
    
    # Test that each domain has the correct structure
    for domain in domains:
        assert "domain" in domain
        assert "is_available" in domain
        assert "price" in domain
        assert isinstance(domain["is_available"], bool)
        assert isinstance(domain["price"], (int, float))

def test_domain_relevance():
    company = "destilabs"
    description = "an outsource company"
    keywords = ["AI"]
    
    domains = generate_domains(company, description, keywords)
    
    # Check if domains contain relevant terms
    relevant_terms = ["destilabs", "desti", "labs", "ai", "outsource", "tech"]
    
    relevant_domains = 0
    for domain in domains:
        domain_name = domain["domain"].lower()
        if any(term in domain_name for term in relevant_terms):
            relevant_domains += 1
    
    # At least 80% of domains should contain relevant terms
    assert relevant_domains >= 12  # 80% of 15

def test_domain_format():
    domains = generate_domains("destilabs", "an outsource company", ["AI"])
    
    for domain in domains:
        domain_name = domain["domain"]
        assert re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', domain_name)


def test_input_variations():
    # Test that different inputs produce different results
    domains1 = generate_domains("destilabs", "an outsource company", ["AI"])
    domains2 = generate_domains("techstar", "a software development company", ["cloud"])
    
    domain_names1 = set(d["domain"] for d in domains1)
    domain_names2 = set(d["domain"] for d in domains2)
    
    assert len(domain_names1.intersection(domain_names2)) < 5  # Less than 1/3 overlap
