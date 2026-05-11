from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


def setup_project_root():
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))


def setup_app(tmp_path, monkeypatch, db_name):
    setup_project_root()
    dbfile = tmp_path / db_name
    monkeypatch.setenv("DB_PATH", str(dbfile))

    import importlib
    import main
    import get_conn
    from init_db import init_db

    importlib.reload(get_conn)
    importlib.reload(main)
    init_db()
    return main


def test_invalid_nivel_foco(tmp_path, monkeypatch):
    main = setup_app(tmp_path, monkeypatch, "test_err.db")

    with TestClient(main.app) as client:
        payload = {"nivel_foco": 6, "tempo_minutos": 10, "comentario": "x"}
        r = client.post("/registro-foco", json=payload)
        assert r.status_code == 422


def test_tempo_non_positive(tmp_path, monkeypatch):
    main = setup_app(tmp_path, monkeypatch, "test_err2.db")

    with TestClient(main.app) as client:
        payload = {"nivel_foco": 3, "tempo_minutos": 0, "comentario": "ok"}
        r = client.post("/registro-foco", json=payload)
        assert r.status_code == 422


def test_empty_comment_returns_400(tmp_path, monkeypatch):
    main = setup_app(tmp_path, monkeypatch, "test_err3.db")

    with TestClient(main.app) as client:
        payload = {"nivel_foco": 3, "tempo_minutos": 10, "comentario": "   "}
        r = client.post("/registro-foco", json=payload)
        assert r.status_code == 400
        assert "comentario" in r.json()["detail"] or "Campo 'comentario'" in r.json()["detail"]


def test_invalid_categoria_enum(tmp_path, monkeypatch):
    main = setup_app(tmp_path, monkeypatch, "test_err4.db")

    with TestClient(main.app) as client:
        payload = {"nivel_foco": 3, "tempo_minutos": 10, "comentario": "ok", "categoria": "invalid"}
        r = client.post("/registro-foco", json=payload)
        assert r.status_code == 422


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"nivel_foco": 3, "tempo_minutos": 10, "comentario": "ab"}, "comentario"),
        ({"nivel_foco": 3, "tempo_minutos": 10, "comentario": "a" * 1001}, "comentario"),
        ({"nivel_foco": 3, "tempo_minutos": 10, "comentario": "ok", "tags": [" "]}, "tags"),
    ],
)
def test_invalid_comment_and_tag_boundaries(tmp_path, monkeypatch, payload, field):
    main = setup_app(tmp_path, monkeypatch, "test_err_boundaries.db")

    with TestClient(main.app) as client:
        response = client.post("/registro-foco", json=payload)
        assert response.status_code == 422
        assert field in str(response.json())


@pytest.mark.parametrize(
    "payload",
    [
        {"nivel_foco": 1, "tempo_minutos": 1, "comentario": "abc"},
        {"nivel_foco": 5, "tempo_minutos": 999, "comentario": "a" * 1000, "tags": ["x"], "categoria": "coding"},
    ],
)
def test_valid_boundary_payloads(tmp_path, monkeypatch, payload):
    main = setup_app(tmp_path, monkeypatch, "test_valid_boundaries.db")

    with TestClient(main.app) as client:
        response = client.post("/registro-foco", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["nivel_foco"] == payload["nivel_foco"]
        assert body["tempo_minutos"] == payload["tempo_minutos"]
        assert body["comentario"] == payload["comentario"].strip()
