import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

class Article(BaseModel):
    name: str

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

memory_db = {"articles": []}

@app.get("/articles", response_model=Articles)
def get_articles():
    return Articles(articles=memory_db["articles"])

@app.post("/articles")
def add_fruit(article: Article):
    memory_db["articles"].append(article)
    return article
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)