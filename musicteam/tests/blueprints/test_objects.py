def test_objects_upload_file(client, mock_storage):
    response = client.http.post(
        "/objects", body=b"12345", headers={"Content-Type": "text/plain"}
    )
    storage_id = response.json_body["id"]

    assert mock_storage.data[storage_id] == b"12345"

    response = client.http.post(
        "/objects?base64=true", body=b"MTIzNDUK", headers={"Content-Type": "text/plain"}
    )
    storage_id = response.json_body["id"]

    assert mock_storage.data[storage_id] == b"12345\n"


def test_objects_upload_file_direct(client, mock_storage):
    response = client.http.post("/objects/direct", json={"content_type": "video/mp4"})
    assert response.json_body["url"] == "https://example.com/"
    assert response.json_body["fields"]["Content-Type"] == "video/mp4"
