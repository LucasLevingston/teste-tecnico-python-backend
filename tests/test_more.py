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


def create_records(client, records):
    for r in records:
        resp = client.post("/registro-foco", json=r)
        assert resp.status_code == 201


def test_diagnostico_various_ranges(tmp_path, monkeypatch):
    main = setup_app(tmp_path, monkeypatch, "test_more.db")

    with TestClient(main.app) as client:
        
        records = [
            {"nivel_foco": 5, "tempo_minutos": 60, "comentario": "task one"},
            {"nivel_foco": 5, "tempo_minutos": 30, "comentario": "task two"},
        ]
        create_records(client, records)
        d = client.get("/diagnostico-produtividade").json()
        assert "maratona produtiva" in d["mensagem"]

    
    main = setup_app(tmp_path, monkeypatch, "test_more2.db")
    with TestClient(main.app) as client:
        records = [
            {"nivel_foco": 3, "tempo_minutos": 20, "comentario": "work A"},
            {"nivel_foco": 4, "tempo_minutos": 40, "comentario": "work B"},
        ]
        create_records(client, records)
        d = client.get("/diagnostico-produtividade").json()
        assert "Produtividade razoável" in d["mensagem"] or "Ótimo foco" in d["mensagem"]

    
    main = setup_app(tmp_path, monkeypatch, "test_more3.db")
    with TestClient(main.app) as client:
        records = [
            {"nivel_foco": 1, "tempo_minutos": 10, "comentario": "low1"},
            {"nivel_foco": 1, "tempo_minutos": 15, "comentario": "low2"},
        ]
        create_records(client, records)
        d = client.get("/diagnostico-produtividade").json()
        assert "Nível de foco baixo" in d["mensagem"]


@pytest.mark.parametrize(
    ("records", "expected_message"),
    [
        ([{"nivel_foco": 5, "tempo_minutos": 10, "comentario": "aaa"}, {"nivel_foco": 4, "tempo_minutos": 10, "comentario": "bbb"}], "maratona produtiva"),
        ([{"nivel_foco": 5, "tempo_minutos": 10, "comentario": "aaa"}, {"nivel_foco": 3, "tempo_minutos": 10, "comentario": "bbb"}], "Ótimo foco"),
        ([{"nivel_foco": 4, "tempo_minutos": 10, "comentario": "aaa"}, {"nivel_foco": 2, "tempo_minutos": 10, "comentario": "bbb"}], "Produtividade razoável"),
        ([{"nivel_foco": 3, "tempo_minutos": 10, "comentario": "aaa"}, {"nivel_foco": 1, "tempo_minutos": 10, "comentario": "bbb"}], "Médio-baixo"),
        ([{"nivel_foco": 1, "tempo_minutos": 10, "comentario": "aaa"}, {"nivel_foco": 1, "tempo_minutos": 10, "comentario": "bbb"}], "Nível de foco baixo"),
    ],
)
def test_diagnostico_message_boundaries(tmp_path, monkeypatch, records, expected_message):
    main = setup_app(tmp_path, monkeypatch, "test_boundaries.db")

    with TestClient(main.app) as client:
        create_records(client, records)
        from diagnostico import diagnostico_produtividade

        diagnostico = diagnostico_produtividade()
        assert expected_message in diagnostico["mensagem"]
        assert expected_message in client.get("/diagnostico-produtividade").json()["mensagem"]


def test_diagnostico_sem_registros(tmp_path, monkeypatch):
    main = setup_app(tmp_path, monkeypatch, "test_empty.db")

    with TestClient(main.app) as client:
        from diagnostico import diagnostico_produtividade

        diagnostico = diagnostico_produtividade()
        assert diagnostico["media_nivel_foco"] is None
        assert diagnostico["tempo_total_minutos"] == 0
        assert diagnostico["registros"] == 0
        assert diagnostico["top_categorias_por_tempo"] == []
        assert "Nenhum registro encontrado" in diagnostico["mensagem"]
        assert "Nenhum registro encontrado" in client.get("/diagnostico-produtividade").json()["mensagem"]


def test_normalize_tags_function():
    
    from normalize_tags import normalize_tags

    assert normalize_tags(None) is None
    assert normalize_tags([]) is None
    assert normalize_tags(["a", " b ", ""]) == "a,b"
    assert normalize_tags(["   ", ""]) == ""


def test_generic_exception_handler_returns_500(tmp_path, monkeypatch):
    main = setup_app(tmp_path, monkeypatch, "test_boom.db")

    import asyncio
    from main import generic_exception_handler

    def boom():
        raise RuntimeError("boom")

    main.app.add_api_route("/boom", boom, methods=["GET"])

    with TestClient(main.app, raise_server_exceptions=False) as client:
        response = client.get("/boom")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"

    response = asyncio.run(generic_exception_handler(None, RuntimeError("boom")))
    assert response.status_code == 500
    assert response.body is not None
