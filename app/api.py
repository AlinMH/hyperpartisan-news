from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from newsplease import NewsPlease
from pydantic import BaseModel


class ClassificationReport(BaseModel):
    title: str
    confidence: float
    class_: str


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


def get_article_info(url):
    article = NewsPlease.from_url(url)
    return article.title, article.maintext


@app.get("/predict", response_model=ClassificationReport)
async def predict_news(url: str):
    title, body = get_article_info(url)
    return ClassificationReport(
        title=title,
        confidence=0.89,
        class_="c"
    )
