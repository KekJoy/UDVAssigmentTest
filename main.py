from fastapi import FastAPI

from comments.comments import comments_router
from news.news import news_router
from loader.data_loader import loader_router

app = FastAPI(title="UDV Assigment Test ValiullinAO")

@app.get("/")
async def foo():
    return {"message": "bar"}

app.include_router(news_router, tags=["news"])
app.include_router(comments_router, tags=["comments"])
app.include_router(loader_router, tags=["loader"])
