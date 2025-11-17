"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the varsity soccer team for practice and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu", "ava@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim laps and train for competitive swimming events",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and various art mediums",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "liam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and learn acting techniques",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills through debates",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 24,
            "participants": ["benjamin@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        
    def test_get_activities_has_correct_participants(self, client):
        """Test that activities have the correct participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Chess Club"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]
        
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student already signed up for this activity"
        
    def test_signup_increases_participant_count(self, client):
        """Test that signup increases the participant count"""
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Chess Club"]["participants"])
        
        # Sign up
        client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        
        # Verify count increased
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successfully(self, client):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Removed michael@mergington.edu from Chess Club"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_unregister_non_participant(self, client):
        """Test unregister for a student not signed up for the activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
        
    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister decreases the participant count"""
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Chess Club"]["participants"])
        
        # Unregister
        client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        
        # Verify count decreased
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1
        
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signup and unregister"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participants
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()[activity]["participants"].copy()
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        activities_response = client.get("/activities")
        final_participants = activities_response.json()[activity]["participants"]
        assert email not in final_participants
        assert final_participants == initial_participants
