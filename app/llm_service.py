
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def generate_briefing(
    topic,
    company,
    format_type,
    articles,
    memory_context=""
):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ValueError("Gemini API key is missing from .env")

    if not articles:
        raise ValueError("No business information was collected.")

    source_text = ""

    for article in articles:
        source_text += (
            f"\nTitle: {article.get('title', 'Untitled')}\n"
            f"URL: {article.get('url', '')}\n"
            f"Content: {article.get('content', '')[:2000]}\n"
        )

    prompt = f"""
You are ExecutiveIntel AI, a professional executive intelligence assistant.

Company or Industry: {company}
Intelligence Category: {topic}
Preferred Format: {format_type}

Previous Executive Preferences and Memory:
{memory_context}

Collected Business Information:
{source_text}

Prepare a professional executive briefing containing:

1. Important business developments.
2. Opportunities and risks.
3. Business impact.
4. Practical recommendations.
5. Relevant personalization based on saved preferences.
6. Source URLs.

Do not invent facts or statistics.
Clearly mention when information is insufficient.
Use clear headings and concise professional language.
"""

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60000)
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text

    except Exception as error:
        raise Exception(f"Gemini generation failed: {error}")

    finally:
        client.close()
