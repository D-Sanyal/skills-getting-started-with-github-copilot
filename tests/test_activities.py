import copy

import pytest
from fastapi.testclient import TestClient

from app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def reset_activities():
    original = copy.deepcopy(activities)
    activities.clear()
    activities.update(copy.deepcopy(original))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_activity_catalog(client, reset_activities):
    # Arrange
    # The in-memory catalog is already populated.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_new_participant(client, reset_activities):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Gym Class/signup?email=newstudent@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Gym Class"
    assert email in activities["Gym Class"]["participants"]


def test_duplicate_signup_returns_conflict(client, reset_activities):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "Student is already signed up"


def test_unregister_participant_removes_email_from_activity(client, reset_activities):
    # Arrange
    email = "john@mergington.edu"

    # Act
    response = client.delete(f"/activities/Gym Class/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Gym Class"
    assert email not in activities["Gym Class"]["participants"]
