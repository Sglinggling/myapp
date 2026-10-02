"""Tests E2E : ils tapent en HTTP sur l'application réellement lancée (conteneur Docker)."""
import os
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8016")


def test_app_is_up():
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_home_page():
    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200
    assert "MyApp" in r.text


def test_user_journey_add_items_and_get_total():
    # Parcours : on ajoute 2 articles, on les liste, on vérifie le total
    before = requests.get(f"{BASE_URL}/total", timeout=5).json()["total"]

    r1 = requests.post(f"{BASE_URL}/items", json={"name": "Souris", "price": 20}, timeout=5)
    r2 = requests.post(f"{BASE_URL}/items", json={"name": "Écran", "price": 150.5}, timeout=5)
    assert r1.status_code == 201 and r2.status_code == 201

    names = [i["name"] for i in requests.get(f"{BASE_URL}/items", timeout=5).json()]
    assert "Souris" in names and "Écran" in names

    after = requests.get(f"{BASE_URL}/total", timeout=5).json()["total"]
    assert round(after - before, 2) == 170.5
