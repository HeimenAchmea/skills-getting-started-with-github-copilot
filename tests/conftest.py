"""
Test configuration and shared fixtures for all tests.
Uses Arrange-Act-Assert (AAA) pattern with pytest fixtures for test isolation.
"""

import pytest
from starlette.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def activities_db():
    """
    Arrange: Provides a clean copy of activities database for each test.
    Resets the global activities dictionary to its initial state before each test.
    """
    # Store initial state
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 4,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 2,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice team play and compete in interschool basketball games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "nina@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swim strokes and conditioning in the school pool",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 1,
            "participants": ["liam@mergington.edu", "maria@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["hannah@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Society": {
            "description": "Learn acting, stagecraft, and perform school productions",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "mason@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore science topics beyond the classroom",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Advanced Math Olympiad": {
            "description": "Solve challenging math problems and prepare for competitions",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["mia@mergington.edu", "jack@mergington.edu"]
        }
    }
    
    # Reset global activities to initial state
    activities.clear()
    activities.update(initial_activities)
    
    yield activities
    
    # Cleanup: reset after test completes
    activities.clear()
    activities.update(initial_activities)


@pytest.fixture
def client(activities_db):
    """
    Arrange: Provides a TestClient instance for making HTTP requests to the app.
    Depends on activities_db fixture to ensure clean state for each test.
    """
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """
    Arrange: Provides sample activity data for unit tests.
    """
    return {
        "description": "Test activity description",
        "schedule": "Test schedule",
        "max_participants": 5,
        "participants": []
    }


@pytest.fixture
def sample_email():
    """
    Arrange: Provides a sample email for testing signup/unregister operations.
    """
    return "test@mergington.edu"
