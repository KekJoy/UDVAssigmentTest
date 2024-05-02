from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from comments.repository import CommentsRepository
from comments.schemas import BaseCommentModel
from news.repository import NewsRepository

comments_router = APIRouter(prefix="/comments", tags=["comments"])


@comments_router.post("",
                      response_model=BaseCommentModel,
                      name="comment post")
async def add_comment(comment: BaseCommentModel,
                      comments_repo: Annotated[CommentsRepository, Depends(CommentsRepository)],
                      news_repo: Annotated[NewsRepository, Depends(NewsRepository)]) -> BaseCommentModel:
    """
    Add a comment on the news
    """
    comment_dict = comment.model_dump()
    if not await news_repo.find_one(comment_dict["news_id"]):
        raise HTTPException(status_code=404, detail="News with this ID does not exist")
    await comments_repo.add_one(comment_dict)
    return comment
