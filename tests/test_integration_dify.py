import re

from tools.utils import generate_domains


def test_domain_list_structure():
    domains_count = 3
    domains = generate_domains("destilabs", "an outsource company", "AI", domains_count)

    assert len(domains) == domains_count

    for domain in domains:
        assert "name" in domain
        assert "price" in domain
        assert isinstance(domain["name"], str)
        assert isinstance(domain["price"], (int, float))


def test_domain_relevance():
    company = "destilabs"
    description = "an outsource company"
    keywords = "AI"
    count = 15

    domains = generate_domains(company, description, keywords, count)

    relevant_terms = ["destilabs", "desti", "labs", "ai", "outsource", "tech"]

    relevant_domains = 0
    for domain in domains:
        domain_name = domain["name"].lower()
        if any(term in domain_name for term in relevant_terms):
            relevant_domains += 1

    assert relevant_domains >= count * 0.8  # 80%


def test_domain_format():
    count = 5
    domains = generate_domains("destilabs", "an outsource company", "AI", count)

    for domain in domains:
        domain_name = domain["name"]
        assert re.match(
            r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$",
            domain_name,
        )
        _, tld = domain_name.split(".", maxsplit=1)
        assert tld == "com"


def test_input_variations():
    count = 15
    domains1 = generate_domains("destilabs", "an outsource company", "AI", count)
    domains2 = generate_domains(
        "techstar", "a software development company", "cloud", count
    )

    domain_names1 = set(d["name"] for d in domains1)
    domain_names2 = set(d["name"] for d in domains2)

    assert len(domain_names1.intersection(domain_names2)) < count // 3
