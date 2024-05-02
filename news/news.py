from typing import Dict, Any, Sequence, Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from comments.repository import CommentsRepository
from news.repository import NewsRepository
from news.schemas import BaseNewsModel, GetNewsModel, GetNewsCommentsModel, GetNewsListModel

news_router = APIRouter(prefix="/news", tags=['news'])


@news_router.post("",
                  response_model=BaseNewsModel,
                  name="news_post")
async def create_news(news: BaseNewsModel,
                      news_repo: Annotated[NewsRepository, Depends(NewsRepository)]
                      ) -> BaseNewsModel:
    """
    Creating a news item
    """
    news_dict = news.model_dump()
    await news_repo.add_one(news_dict)
    return news


@news_router.delete("",
                    response_model=GetNewsModel,
                    name="news_delete",
                    responses={
                        status.HTTP_404_NOT_FOUND: {
                            "description": "News with this ID does not exist or it has been deleted"}
                    })
async def delete_news(id: int,
                      news_repo: Annotated[NewsRepository, Depends(NewsRepository)]
                      ):
    """
    Assign "Deleted" status to a news item
    """
    if not await news_repo.find_one(record_id=id):
        raise HTTPException(status_code=404, detail="News with this ID does not exist or it has been deleted")
    await news_repo.update_one(record_id=id, data={"is_deleted": True})
    return await news_repo.find_one(record_id=id)


@news_router.patch("",
                   response_model=GetNewsModel,
                   name="news_patch",
                   responses={
                       status.HTTP_404_NOT_FOUND: {
                           "description": "News with this ID does not exist or it has been"}
                   })
async def update_news(news: BaseNewsModel,
                      news_id: int,
                      news_repo: Annotated[NewsRepository, Depends(NewsRepository)]
                      ) -> BaseNewsModel:
    """
    Update the news data
    """
    news_dict = news.model_dump()
    if not await news_repo.find_one(record_id=news_id):
        raise HTTPException(status_code=404, detail="News with this ID does not exist or it has been")
    await news_repo.update_one(record_id=news_id, data=news_dict)
    return await news_repo.find_one(record_id=news_id)


@news_router.get("",
                 response_model=GetNewsListModel,
                 name="news_list"
                 )
async def get_news(news_repo: Annotated[NewsRepository, Depends(NewsRepository)],
                   comments_repo: Annotated[CommentsRepository, Depends(CommentsRepository)]
                   ) -> dict[str, int | Any]:
    """
    Get a list of all news
    """
    news = await news_repo.find_all(conditions={"is_deleted": False})
    for element in news:
        element.comments_count = await comments_repo.comments_count(element.id)
    print(news)
    return {"news": news, "news_count": len(news)}


@news_router.get("/{id}",
                 response_model=GetNewsCommentsModel,
                 name="news_comments",
                 responses={
                     status.HTTP_404_NOT_FOUND: {"description": "News with this ID does not exist or it has been"}
                 })
async def get_news_by_id(id: int,
                         comments_repo: Annotated[CommentsRepository, Depends(CommentsRepository)],
                         news_repo: Annotated[NewsRepository, Depends(NewsRepository)]
                         ) -> dict[str, int | Any]:
    """
    Get news by ID
    """
    news = await news_repo.get_one(record_id=id)
    if not news or news.is_deleted == True:
        raise HTTPException(status_code=404, detail="News with this ID does not exist or it has been")
    news.comments_count = await comments_repo.comments_count(news_id=id)
    news.comments = await comments_repo.find_all(conditions={"news_id": id})
    return news
