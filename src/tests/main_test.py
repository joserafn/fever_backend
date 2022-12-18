from pytest import mark
from pytest_asyncio import fixture
from httpx import AsyncClient

from main import app


@fixture
@mark.asyncio
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@mark.asyncio
async def test_search_no_query_params(client):
    response = await client.get("/search")
    assert response.status_code == 400

@mark.asyncio
async def test_search_bad_query_params(client):
    response = await client.get("/search?starts_at=no_valid_date")
    assert response.status_code == 400

@mark.asyncio
async def test_search_with_query_params(client):
    response = await client.get("/search?starts_at=2017-07-21T17%3A32%3A28Z&ends_at=2021-07-21T17%3A32%3A28Z")
    assert response.status_code == 200
    assert len(response.json()) == 2
