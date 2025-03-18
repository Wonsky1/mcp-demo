import re
from tools.utils import generate_domains


def test_domain_generator():
    """Comprehensive test for the domain generator functionality."""
    # Test case 1: Basic structure with destilabs
    company = "destilabs"
    description = "an outsource company"
    keywords = "AI"
    count = 15
    
    domains = generate_domains(company, description, keywords, count)
    
    # Test structure
    assert len(domains) == count
    for domain in domains:
        assert "name" in domain
        assert "price" in domain
        assert isinstance(domain["name"], str)
        assert isinstance(domain["price"], (int, float))
    
    # Test relevance
    relevant_terms = ["destilabs", "desti", "labs", "ai", "outsource", "tech"]
    relevant_domains = sum(
        1 for domain in domains 
        if any(term in domain["name"].lower() for term in relevant_terms)
    )
    assert relevant_domains >= count * 0.8  # 80% should be relevant
    
    # Test format
    for domain in domains:
        domain_name = domain["name"]
        assert re.match(
            r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$",
            domain_name,
        )
        _, tld = domain_name.split(".", maxsplit=1)
        assert tld == "com"
    
    # Test case 2: Input variations
    company2 = "techstar"
    description2 = "a software development company"
    keywords2 = "cloud"
    
    domains2 = generate_domains(company2, description2, keywords2, count)
    
    domain_names1 = set(d["name"] for d in domains)
    domain_names2 = set(d["name"] for d in domains2)
    
    # Different inputs should produce mostly different outputs
    assert len(domain_names1.intersection(domain_names2)) < count // 3
