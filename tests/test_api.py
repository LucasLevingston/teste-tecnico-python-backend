from pathlib import Path
import sys

from fastapi.testclient import TestClient


def test_criar_e_diagnostico(tmp_path, monkeypatch):
    
    dbfile = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(dbfile))

    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    import importlib
    import main
    from init_db import init_db

    importlib.reload(main)
    init_db()

    with TestClient(main.app) as client:
        payload = {
            "nivel_foco": 5,
            "tempo_minutos": 30,
            "comentario": "Implementação de endpoint",
            "categoria": "coding",
            "tags": ["api", "fastapi"],
        }

        r = client.post("/registro-foco", json=payload)
        assert r.status_code == 201
        body = r.json()
        assert body["nivel_foco"] == 5

        d = client.get("/diagnostico-produtividade").json()
        assert d["registros"] == 1
        assert d["tempo_total_minutos"] == 30
