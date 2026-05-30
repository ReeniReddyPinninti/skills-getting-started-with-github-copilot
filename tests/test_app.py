import importlib

from fastapi.testclient import TestClient

import src.app as app_module



def create_client():
    module = importlib.reload(app_module)
    return TestClient(module.app), module



def test_root_redirects_to_static_index():
    client, _ = create_client()

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"



def test_get_activities_returns_seed_data():
    client, module = create_client()

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == module.activities["Chess Club"]["participants"]



def test_signup_adds_participant():
    client, module = create_client()

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up new.student@mergington.edu for Chess Club"
    assert "new.student@mergington.edu" in module.activities["Chess Club"]["participants"]



def test_signup_rejects_duplicate_participant():
    client, _ = create_client()

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"



def test_signup_unknown_activity_returns_404():
    client, _ = create_client()

    response = client.post(
        "/activities/Robotics%20Team/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"



def test_unregister_participant_removes_signup():
    client, module = create_client()

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in module.activities["Chess Club"]["participants"]



def test_unregister_missing_participant_returns_404():
    client, _ = create_client()

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"



def test_unregister_unknown_activity_returns_404():
    client, _ = create_client()

    response = client.delete(
        "/activities/Robotics%20Team/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
