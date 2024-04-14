from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from comments.schemas import GetCommentModel


class BaseNewsModel(BaseModel):
    title: str
    date: datetime
    body: str
    is_deleted: bool = False


class GetNewsModel(BaseNewsModel):
    id: int
    comments_count: int | None = None


class GetNewsListModel(BaseModel):
    news: List[GetNewsModel]
    news_count: int


class GetNewsCommentsModel(GetNewsModel):
    comments: List[GetCommentModel] | None = None
