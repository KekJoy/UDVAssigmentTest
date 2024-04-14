from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from comments.repository import CommentsRepository, Comments
from main import app
from news.news import delete_news
from news.repository import NewsRepository, News


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_news(test_client):
    news_data = {
        "title": "Test News",
        "date": "2024-04-14T12:00:00",
        "body": "This is a test news item.",
        "is_deleted": False
    }

    response = test_client.post("/news", json=news_data)

    assert response.status_code == 200
    created_news = response.json()
    assert created_news["title"] == news_data["title"]
    assert created_news["date"] == news_data["date"]
    assert created_news["body"] == news_data["body"]
    assert created_news["is_deleted"] == news_data["is_deleted"]


@pytest.mark.asyncio
async def test_delete_news_successful(mocker):
    news_instance = News(id=1, title="Test News", date="2024-04-14T12:00:00", body="Some body", is_deleted=True)

    mocker.patch.object(NewsRepository, 'find_one', return_value=news_instance)
    mocker.patch.object(NewsRepository, 'update_one', new_callable=AsyncMock, return_value=1)

    response = await delete_news(id=1)
    assert isinstance(response, News)

    assert response.is_deleted is True


@pytest.mark.asyncio
async def test_delete_news_not_found(mocker):
    mocker.patch.object(NewsRepository, 'find_one', return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await delete_news(id=999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "News with this ID does not exist or it has been deleted"


@pytest.mark.asyncio
async def test_get_news_successful(mocker, test_client):
    fake_news = [
        News(id=1, title="Test News 1", date="2024-04-14T12:00:00", body="Body 1", is_deleted=False),
        News(id=2, title="Test News 2", date="2024-04-15T12:00:00", body="Body 2", is_deleted=False)
    ]

    mocker.patch.object(NewsRepository, 'find_all', return_value=fake_news)

    mocker.patch.object(CommentsRepository, 'comments_count', new_callable=AsyncMock, side_effect=[1, 2])

    response = test_client.get("/news")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["news"]) == 2
    assert response.json()["news_count"] == 2

    assert response.json()["news"][0]["id"] == 1
    assert response.json()["news"][0]["title"] == "Test News 1"
    assert response.json()["news"][0]["date"] == "2024-04-14T12:00:00"
    assert response.json()["news"][0]["body"] == "Body 1"
    assert response.json()["news"][0]["is_deleted"] == False
    assert response.json()["news"][0]["comments_count"] == 1

    assert response.json()["news"][1]["id"] == 2
    assert response.json()["news"][1]["title"] == "Test News 2"
    assert response.json()["news"][1]["date"] == "2024-04-15T12:00:00"
    assert response.json()["news"][1]["body"] == "Body 2"
    assert response.json()["news"][1]["is_deleted"] == False
    assert response.json()["news"][1]["comments_count"] == 2


@pytest.mark.asyncio
async def test_get_news_by_id_successful(mocker, test_client):
    fake_news = News(id=1, title="Test News 1", date="2024-04-14T12:00:00", body="Body 1", is_deleted=False)

    fake_comments = [
        Comments(id=1, news_id=1, title="Comment 1", date="2024-04-14T12:00:00", comment="Comment 1")
    ]

    mocker.patch.object(NewsRepository, 'get_one', return_value=fake_news)

    mocker.patch.object(CommentsRepository, 'comments_count', return_value=1)

    mocker.patch.object(CommentsRepository, 'find_all', return_value=fake_comments)

    response = test_client.get("/news/1")

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["id"] == 1
    assert response.json()["title"] == "Test News 1"
    assert response.json()["date"] == "2024-04-14T12:00:00"
    assert response.json()["body"] == "Body 1"
    assert response.json()["is_deleted"] == False
    assert len(response.json()["comments"]) == 1
    assert response.json()["comments_count"] == 1

    assert response.json()["comments"][0]["id"] == 1
    assert response.json()["comments"][0]["news_id"] == 1
    assert response.json()["comments"][0]["title"] == "Comment 1"
    assert response.json()["comments"][0]["date"] == "2024-04-14T12:00:00"
    assert response.json()["comments"][0]["comment"] == "Comment 1"
