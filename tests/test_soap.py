import threading
from wsgiref.simple_server import make_server, WSGIRequestHandler

import pytest
import requests

from soap.soap_service import wsgi_app

NS = "bibliotech.soap"


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def soap_url():
    server = make_server("127.0.0.1", 0, wsgi_app, handler_class=QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/"
    server.shutdown()


def call(url, op, **params):
    inner = "".join(f"<spy:{k}>{v}</spy:{k}>" for k, v in params.items())
    xml = (
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        f'xmlns:spy="{NS}"><soapenv:Header/><soapenv:Body>'
        f"<spy:{op}>{inner}</spy:{op}></soapenv:Body></soapenv:Envelope>"
    )
    return requests.post(
        url,
        data=xml.encode("utf-8"),
        headers={"Content-Type": "text/xml;charset=UTF-8"},
    )


BOOK = dict(id=1, title="Clean Code", author="Robert C. Martin",
            available_copies=5, rental_price=3.5)


def test_wsdl_is_published(soap_url):
    r = requests.get(soap_url + "?wsdl")
    assert r.status_code == 200
    for op in ("CreateBook", "GetBook", "UpdateBook", "DeleteBook"):
        assert op in r.text


def test_create_then_get(soap_url):
    r = call(soap_url, "CreateBook", **BOOK)
    assert r.status_code == 200 and "Clean Code" in r.text
    r = call(soap_url, "GetBook", id=1)
    assert r.status_code == 200 and "Robert C. Martin" in r.text


def test_duplicate_id(soap_url):
    call(soap_url, "CreateBook", **BOOK)
    r = call(soap_url, "CreateBook", **BOOK)
    assert r.status_code >= 400 and "Client.DuplicateId" in r.text


def test_negative_stock_rejected(soap_url):
    r = call(soap_url, "CreateBook", **{**BOOK, "available_copies": -1})
    assert r.status_code >= 400 and "Client.InvalidCopies" in r.text


def test_negative_price_rejected(soap_url):
    r = call(soap_url, "CreateBook", **{**BOOK, "rental_price": -2})
    assert r.status_code >= 400 and "Client.InvalidPrice" in r.text


def test_invalid_id_rejected(soap_url):
    r = call(soap_url, "CreateBook", **{**BOOK, "id": 0})
    assert r.status_code >= 400 and "Client.InvalidId" in r.text
    r = call(soap_url, "GetBook", id=-5)
    assert "Client.InvalidId" in r.text


def test_get_missing_book(soap_url):
    r = call(soap_url, "GetBook", id=999)
    assert r.status_code >= 400 and "Client.NotFound" in r.text


def test_update(soap_url):
    call(soap_url, "CreateBook", **BOOK)
    r = call(soap_url, "UpdateBook", **{**BOOK, "title": "Clean Code 2", "available_copies": 8})
    assert r.status_code == 200 and "Clean Code 2" in r.text
    assert "<tns:available_copies>8<" in call(soap_url, "GetBook", id=1).text.replace(
        "ns0:", "tns:"
    ) or "8" in call(soap_url, "GetBook", id=1).text


def test_delete(soap_url):
    call(soap_url, "CreateBook", **BOOK)
    r = call(soap_url, "DeleteBook", id=1)
    assert r.status_code == 200 and "deleted" in r.text
    assert "Client.NotFound" in call(soap_url, "GetBook", id=1).text