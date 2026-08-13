from pathlib import Path

from fastapi.testclient import TestClient

import app
from build_db import build


def test_question_api(tmp_path: Path) -> None:
    source = Path(__file__).parents[1] / "web" / "src" / "data" / "questions.json"
    database = tmp_path / "questions.sqlite"
    build(source, database)
    old_database = app.DATABASE
    app.DATABASE = database
    try:
        client = TestClient(app.app)
        assert client.get("/health").json()["ok"] is True
        facets = client.get("/api/facets").json()
        assert facets["total"] > 0
        listing = client.get("/api/questions", params={"q": "derivative", "page_size": 3}).json()
        assert listing["total"] > 0
        assert len(listing["items"]) <= 3
        assert "evidence" not in listing["items"][0]
        detail = client.get(f"/api/questions/{listing['items'][0]['id']}")
        assert detail.status_code == 200
        assert detail.json()["method_path"]
    finally:
        app.DATABASE = old_database
