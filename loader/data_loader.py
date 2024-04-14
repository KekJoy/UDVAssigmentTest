import json
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from comments.repository import CommentsRepository
from comments.schemas import BaseCommentModel
from database import get_async_session
from news.repository import NewsRepository
from news.schemas import GetNewsListModel, BaseNewsModel

loader_router = APIRouter(prefix="/loader", tags=['loader'])


@loader_router.post("/news-load")
async def load_news(news_file: UploadFile = File(...)) -> dict[str, str | Any]:
    """
    Load new news from JSON
    """
    contents = await news_file.read()
    json_data = json.loads(contents)

    try:

        for item in json_data.get("news", []):
            news_data = BaseNewsModel(**item)
            db_news = await NewsRepository().add_one(news_data.dict())

        return {"message": "News added successfully", "data": json_data.get("news", [])}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@loader_router.post("/comments-load")
async def load_comments(comments_file: UploadFile = File(...)) -> dict[str, str | Any]:
    """
    Load comments from JSON
    """
    contents = await comments_file.read()
    json_data = json.loads(contents)

    try:

        for item in json_data.get("comments", []):
            comments_data = BaseCommentModel(**item)
            db_comments = await CommentsRepository().add_one(comments_data.dict())

        return {"message": "Comments added successfully", "data": json_data.get("comments", [])}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))