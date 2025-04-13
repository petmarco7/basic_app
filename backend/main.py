import json
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .database import db
from .logging_config import logger

app = FastAPI()

# CORS settings to allow frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InputData(BaseModel):
    text: str


class HighlightedText(BaseModel):
    word: str
    start: int
    end: int


@app.post("/submit/")
async def receive_data(data: InputData) -> dict:
    msg = f"Received data: {data.text}"
    logger.info(msg)

    query = "INSERT INTO searches (search) VALUES ($1)"
    await db.insert(query, data.text)

    return {"message": "Text received", "text": data.text}


# Send text to the frontend
@app.get("/text/")
async def send_text() -> dict:
    # Get the text from the database
    query = "SELECT text, annotations FROM texts LIMIT 1"
    text = (await db.select(query))[0]

    logger.info(f"Sending text: {text}")

    text = {"text": text["text"], "annotations": text["annotations"] or []}

    # Find tokens and track whether each is followed by whitespace
    matches = re.finditer(r"(\w+|[^\w\s])(\s*)", text["text"])

    # Separate tokens and whitespaces
    tokens = []
    whitespaces = []

    for match in matches:
        tokens.append(match.group(1))
        whitespaces.append(" " if match.group(2) else "")

    whitespaces = whitespaces[:-1]  # Drop the last whitespace

    return {
        "text": text["text"],
        "words": tokens,
        "whitespaces": whitespaces,
        "annotations": text["annotations"],
    }


@app.post("/text_highlight/")
async def highlight_text(data: dict) -> dict:
    msg = f"Received highlighted text: {data}"
    logger.info(msg)

    # Insert the text and annotations into the database
    query = "INSERT INTO annotations (text, annotations) VALUES ($1, $2)"
    await db.insert(query, data["text"], json.dumps(data["annotations"]))

    return {"message": "Text received"}
