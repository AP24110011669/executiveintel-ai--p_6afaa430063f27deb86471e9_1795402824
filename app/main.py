
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.firecrawl_service import search_business_information
from app.llm_service import generate_briefing
from app.memory_service import (
    save_preferences,
    get_preferences,
    save_briefing_history,
    get_briefing_history
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="ExecutiveIntel AI",
    description="Personalized Executive Intelligence Assistant",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


class BriefingRequest(BaseModel):
    topic: str
    company: str
    format: str = "Executive Summary"


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "preferences": get_preferences()
        }
    )


@app.get("/api/health")
async def health():
    return {
        "status": "running",
        "application": "ExecutiveIntel AI",
        "version": "1.0.0"
    }


@app.get("/api")
async def api_home():
    return {
        "message": "Welcome to ExecutiveIntel AI",
        "documentation": "/docs"
    }


@app.post("/api/briefing")
def create_briefing(request: BriefingRequest):

    try:
        articles = search_business_information(
            request.topic,
            request.company
        )

        if not articles:
            raise HTTPException(
                status_code=404,
                detail="No relevant business information found."
            )

        briefing = generate_briefing(
            request.topic,
            request.company,
            request.format,
            articles
        )

        save_preferences(
            request.topic,
            request.company,
            request.format
        )

        save_briefing_history({
            "topic": request.topic,
            "company": request.company,
            "format": request.format,
            "briefing": briefing,
            "sources": [
                {
                    "title": article["title"],
                    "url": article["url"]
                }
                for article in articles
            ]
        })

        return {
            "status": "success",
            "briefing": briefing,
            "sources": [
                {
                    "title": article["title"],
                    "url": article["url"]
                }
                for article in articles
            ]
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.get("/api/preferences")
async def preferences():
    return get_preferences()


@app.get("/api/history")
async def history():
    return get_briefing_history()
