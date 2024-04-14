from datetime import datetime

from pydantic import BaseModel


class BaseCommentModel(BaseModel):
    news_id: int
    title: str
    date: datetime
    comment: str


class GetCommentModel(BaseCommentModel):
    id: int

