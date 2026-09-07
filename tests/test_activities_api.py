from fastapi.testclient import TestClient

from src.app import activities


def test_root_redirects_to_static_page(client: TestClient):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client: TestClient):
    response = client.get("/activities")

    assert response.status_code == 200
    response_activities = response.json()
    assert len(response_activities) == 9
    assert response_activities["Chess Club"] == {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ],
    }


def test_signup_adds_participant(client: TestClient):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Soccer%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Soccer Club",
    }
    assert email in activities["Soccer Club"]["participants"]


def test_signup_rejects_duplicate_participant(client: TestClient):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity",
    }


def test_signup_rejects_unknown_activity(client: TestClient):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client: TestClient):
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club",
    }
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client: TestClient):
    response = client.delete(
        "/activities/Soccer%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity",
    }


def test_unregister_rejects_unknown_activity(client: TestClient):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}