
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_briefing(topic, company, format_type, articles):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ValueError("Gemini API key is missing from .env")

    if not articles:
        raise ValueError("No business information was collected.")

    client = genai.Client(api_key=api_key)

    source_text = ""

    for article in articles:
        source_text += (
            f"\nTitle: {article['title']}\n"
            f"URL: {article['url']}\n"
            f"Content: {article['content'][:3000]}\n"
        )

    prompt = f"""
You are ExecutiveIntel AI, a professional executive intelligence assistant.

Company or Industry: {company}
Intelligence Category: {topic}
Preferred Format: {format_type}

Collected Information:
{source_text}

Instructions:
1. Summarize important developments.
2. Identify business opportunities and risks.
3. Explain why the information matters to executives.
4. Give practical recommendations.
5. Do not invent facts or statistics.
6. Mention when information is insufficient.
7. Include source URLs wherever relevant.

Write in a clear, professional executive style.
"""

    try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                if not response.text:
                    raise ValueError("Gemini returned an empty response.")

                return response.text

            except Exception as error:
                error_message = str(error).upper()

                temporary_error = (
                    "503" in error_message
                    or "UNAVAILABLE" in error_message
                )

                if temporary_error and attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue

                raise

    finally:
        client.close()
