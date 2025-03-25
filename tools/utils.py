import requests
from core.config import settings


def generate_domains(
    name: str, description: str = "", keywords: str = "", count: int = 15
) -> dict:
    url = settings.DIFY_WORKFLOW_URL
    headers = {
        "Authorization": f"Bearer {settings.DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "inputs": {
            "name": name,
            "description": description,
            "keywords": keywords,
            "count": count,
        },
        "response_mode": "blocking",
        "user": "test-user",
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        
        if (
            json_response.get("data")
            and json_response["data"].get("outputs")
            and json_response["data"]["outputs"].get("output")
        ):
            return json_response["data"]["outputs"]["output"]
        else:
            # Log the error properly
            print(f"API returned unexpected response structure: {json_response}")
            return {}
    except requests.exceptions.RequestException as e:
        # Log the error properly
        print(f"Error making request to Dify API: {str(e)}")
        return {}
