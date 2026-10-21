from fastapi.testclient import TestClient

from soap.rest_api import soap

client = TestClient(soap)

BOOK = {"id": 1, "title": "Clean Code", "author": "Robert C. Martin",
        "available_copies": 5, "rental_price": 3.5}


def test_create_and_list():
    r = client.post("/books", json=BOOK)
    assert r.status_code == 201 and r.json() == BOOK
    r = client.get("/books")
    assert r.status_code == 200 and r.json() == [BOOK]


def test_duplicate_id_conflict():
    client.post("/books", json=BOOK)
    assert client.post("/books", json=BOOK).status_code == 409


def test_negative_stock_rejected():
    assert client.post("/books", json={**BOOK, "available_copies": -1}).status_code == 422


def test_negative_price_rejected():
    assert client.post("/books", json={**BOOK, "rental_price": -0.5}).status_code == 422


def test_invalid_id_rejected():
    assert client.post("/books", json={**BOOK, "id": 0}).status_code == 422
    assert client.delete("/books/0").status_code == 422


def test_empty_title_rejected():
    assert client.post("/books", json={**BOOK, "title": "  "}).status_code == 422


def test_update():
    client.post("/books", json=BOOK)
    new = {k: v for k, v in BOOK.items() if k != "id"} | {"title": "Clean Code 2", "available_copies": 8}
    r = client.put("/books/1", json=new)
    assert r.status_code == 200
    assert r.json()["title"] == "Clean Code 2" and r.json()["available_copies"] == 8


def test_update_missing_book():
    new = {k: v for k, v in BOOK.items() if k != "id"}
    assert client.put("/books/42", json=new).status_code == 404


def test_delete():
    client.post("/books", json=BOOK)
    assert client.delete("/books/1").status_code == 204
    assert client.delete("/books/1").status_code == 404
    assert client.get("/books").json() == []


def test_openapi_is_generated():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "/books" in r.json()["paths"]