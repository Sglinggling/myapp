import pytest
from app.main import app, compute_total, items


@pytest.fixture
def client():
    items.clear()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_compute_total():
    assert compute_total([10, 5.5, 4.5]) == 20
    assert compute_total([]) == 0


def test_compute_total_negative():
    with pytest.raises(ValueError):
        compute_total([10, -1])


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_add_and_list_items(client):
    r = client.post("/items", json={"name": "Clavier", "price": 79.99})
    assert r.status_code == 201
    assert r.get_json()["name"] == "Clavier"
    assert len(client.get("/items").get_json()) == 1


def test_add_item_invalid(client):
    r = client.post("/items", json={"name": "Sans prix"})
    assert r.status_code == 400
