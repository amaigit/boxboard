import pytest
from httpx import AsyncClient
from api import app


@pytest.mark.asyncio
async def test_healthcheck():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_login_and_crud():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Crea utente admin di test (se non esiste)
        # NB: in un test reale, dovresti popolare il DB di test o mockare
        # Login
        resp = await ac.post(
            "/login", data={"username": "admin@test.com", "password": "admin@test.com"}
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # CRUD utenti (solo GET qui per esempio)
        resp = await ac.get("/utenti", headers=headers)
        assert resp.status_code == 200
        # CRUD location
        loc = {"nome": "LocTest", "indirizzo": "Via Test", "note": "Test"}
        resp = await ac.post("/locations", json=loc, headers=headers)
        assert resp.status_code == 200
        loc_id = resp.json()["id"]
        resp = await ac.get(f"/locations/{loc_id}", headers=headers)
        assert resp.status_code == 200
        # CRUD oggetti
        obj = {"nome": "OggettoTest", "location_id": loc_id}
        resp = await ac.post("/oggetti", json=obj, headers=headers)
        assert resp.status_code == 200
        obj_id = resp.json()["id"]
        resp = await ac.get(f"/oggetti/{obj_id}", headers=headers)
        assert resp.status_code == 200
        # CRUD attività
        att = {"nome": "AttTest"}
        resp = await ac.post("/attivita", json=att, headers=headers)
        assert resp.status_code == 200
        att_id = resp.json()["id"]
        resp = await ac.get(f"/attivita/{att_id}", headers=headers)
        assert resp.status_code == 200
        # CRUD note
        nota = {"testo": "NotaTest", "oggetto_id": obj_id}
        resp = await ac.post("/note", json=nota, headers=headers)
        assert resp.status_code == 200
        nota_id = resp.json()["id"]
        resp = await ac.get(f"/note/{nota_id}", headers=headers)
        assert resp.status_code == 200
        # Cleanup
        await ac.delete(f"/note/{nota_id}", headers=headers)
        await ac.delete(f"/attivita/{att_id}", headers=headers)
        await ac.delete(f"/oggetti/{obj_id}", headers=headers)
        await ac.delete(f"/locations/{loc_id}", headers=headers)
