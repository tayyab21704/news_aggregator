import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid
from datetime import datetime

class Article(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    link: str
    source: str
    authors: List[str] | None = None
    summary: str | None = None
    text: str | None = None
    top_image_url: str | None = None
    keywords: List[str] | None = None
    published_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CreateArticlePayload(BaseModel):
    """A model for the article data coming from the RSS feed."""
    title: str
    link: str  # from 'url'
    source: str
    authors: List[str] | None = None
    published_at: datetime | None = None  # from 'publish_date'
    summary: str | None = None
    text: str | None = None
    top_image_url: str | None = None  # from 'top_image'
    keywords: List[str] | None = None

class Articles(BaseModel):
    articles: List[Article]

app = FastAPI(debug=True)

origins = [
    "http://localhost:5173",
    # Add more origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using a dictionary with UUIDs as keys for efficient lookups
memory_db: Dict[uuid.UUID, Article] = {}

@app.get("/articles", response_model=Articles)
def get_articles():
    return Articles(articles=list(memory_db.values()))

@app.get("/articles/{article_id}", response_model=Article)
def get_article(article_id: uuid.UUID):
    return memory_db.get(article_id)

@app.post("/articles", response_model=Article, status_code=status.HTTP_201_CREATED)
def create_article(payload: CreateArticlePayload):
    # Use model_dump() to easily transfer data from payload to the main model
    new_article = Article(**payload.model_dump())
    memory_db[new_article.id] = new_article
    return new_article

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
