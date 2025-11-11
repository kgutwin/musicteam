def test_base(client):
    response = client.http.get("/")
    assert response.json_body == {"status": "tbd"}
