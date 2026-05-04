"""
Integration tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
Tests the full HTTP request/response cycle for listing all activities.
"""

import pytest


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_success(self, client):
        """
        Arrange: Have a test client
        Act: Make a GET request to /activities
        Assert: Response status should be 200
        """
        # Arrange - client fixture is already set up
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """
        Arrange: Have a test client
        Act: Make a GET request to /activities
        Assert: Response body should be a dictionary
        """
        # Arrange
        expected_type = dict
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, expected_type)
    
    def test_get_activities_contains_all_activities(self, client):
        """
        Arrange: Have a test client
        Act: Make a GET request to /activities
        Assert: Response should contain all expected activities
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Swimming Club",
            "Art Club",
            "Drama Society",
            "Science Club",
            "Advanced Math Olympiad"
        ]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name in expected_activities:
            assert activity_name in data
    
    def test_activity_has_required_fields(self, client):
        """
        Arrange: Have a test client
        Act: Make a GET request to /activities
        Assert: Each activity should have required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert set(activity_data.keys()) == required_fields
    
    def test_activity_fields_have_correct_types(self, client):
        """
        Arrange: Have a test client
        Act: Make a GET request to /activities and check Chess Club structure
        Assert: Fields should have the correct data types
        """
        # Arrange - expected types
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)
    
    def test_activity_participants_are_strings(self, client):
        """
        Arrange: Have a test client
        Act: Make a GET request to /activities
        Assert: All participants should be strings (emails)
        """
        # Arrange
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
    
    def test_max_participants_is_positive(self, client):
        """
        Arrange: Have a test client
        Act: Make a GET request to /activities
        Assert: max_participants should always be positive
        """
        # Arrange
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert activity_data["max_participants"] > 0
