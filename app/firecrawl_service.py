
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def search_business_information(topic, company):
    api_key = os.getenv("FIRECRAWL_API_KEY", "").strip()

    if not api_key:
        raise ValueError("Firecrawl API key is missing from .env")

    url = "https://api.firecrawl.dev/v2/search"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": f"{company} {topic} latest business news",
        "limit": 3
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=(10, 30)
        )

        response.raise_for_status()
        result = response.json()

        data = result.get("data", {})
        articles = data.get("web", []) if isinstance(data, dict) else []

        information = []

        for article in articles:
            information.append({
                "title": article.get("title") or "Untitled",
                "url": article.get("url") or "",
                "content": article.get("description") or ""
            })

        return information

    except requests.Timeout:
        raise Exception(
            "Firecrawl took too long to respond. Please try again."
        )

    except requests.RequestException as error:
        raise Exception(f"Firecrawl error: {error}")

    except ValueError as error:
        raise Exception(f"Invalid Firecrawl response: {error}")
