import pytest


@pytest.mark.asyncio
async def test_admin_can_create_notification(test_client):
    response = await test_client.post(
        "/notifications/",
        json={"text": "Test create", "comment": "Test create"}
    )
    notif_id = response.json()["id"]
    await test_client.delete(f"/notifications/{notif_id}")
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Test create"


@pytest.mark.asyncio
async def test_admin_can_edit_notification(test_client):
    create_resp = await test_client.post(
        "/notifications/",
        json={"text": "Test edit", "comment": "Test edit"}
    )
    notif_id = create_resp.json()["id"]
    response = await test_client.put(
        f"/notifications/{notif_id}",
        json={"text": "Edited complite"}
    )
    await test_client.delete(f"/notifications/{notif_id}")
    assert response.status_code == 200
    assert response.json()["text"] == "Edited complite"


@pytest.mark.asyncio
async def test_admin_can_delete_notification(test_client):
    create_resp = await test_client.post(
        "/notifications/",
        json={"text": "Test delete", "comment": "Test delete"}
    )
    notif_id = create_resp.json()["id"]
    response = await test_client.delete(f"/notifications/{notif_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_admin_list_notifications(test_client):
    response = await test_client.get("/notifications/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
