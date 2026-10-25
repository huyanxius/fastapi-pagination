import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from fastapi_pagination import add_pagination, paginate
from fastapi_pagination.customization import CustomizedPage
from fastapi_pagination.limit_offset import LimitOffsetPage
from fastapi_pagination.links import UseLimitOffsetHeaderLinks, UseLimitOffsetLinks


@pytest.mark.parametrize("header_links", [False, True], ids=["body", "header"])
@pytest.mark.parametrize("only_path", [False, True, None], ids=["absolute", "relative", "default"])
def test_limit_offset_links_only_path(header_links, only_path):
    customizer = UseLimitOffsetHeaderLinks if header_links else UseLimitOffsetLinks
    page_cls = CustomizedPage[
        LimitOffsetPage[int],
        customizer() if only_path is None else customizer(only_path=only_path),
    ]
    app = FastAPI()

    @app.get("/items", response_model=page_cls)
    async def route():
        return paginate([*range(6)])

    add_pagination(app)
    client = TestClient(app, base_url="https://pagination.example:8443")
    response = client.get("/items?limit=2&offset=2&filter=kept")

    assert response.status_code == status.HTTP_200_OK
    prefix = "https://pagination.example:8443" if only_path is False else ""
    expected = {
        "first": f"{prefix}/items?limit=2&filter=kept&offset=0",
        "last": f"{prefix}/items?limit=2&filter=kept&offset=4",
        "next": f"{prefix}/items?limit=2&filter=kept&offset=4",
        "prev": f"{prefix}/items?limit=2&filter=kept&offset=0",
    }
    if header_links:
        assert {rel: value["url"] for rel, value in response.links.items()} == expected
    else:
        assert response.json()["links"] == {
            **expected,
            "self": f"{prefix}/items?limit=2&offset=2&filter=kept",
        }
