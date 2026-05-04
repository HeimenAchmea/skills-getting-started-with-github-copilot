"""
Integration tests for POST /activities/{activity_name}/signup endpoint using AAA pattern.
Tests signup functionality with success cases, validation, and error scenarios.
"""

import pytest


class TestSignupSuccessful:
    """Tests for successful signup scenarios"""
    
    def test_signup_successful_with_valid_data(self, client, sample_email):
        """
        Arrange: Have a fresh activity with available space and a test email
        Act: POST signup request with valid activity and email
        Assert: Response status should be 200 and student should be added
        """
        # Arrange
        activity_name = "Basketball Team"
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = len(updated_response.json()[activity_name]["participants"])
        assert updated_participants == initial_participants + 1
    
    def test_signup_response_contains_confirmation_message(self, client, sample_email):
        """
        Arrange: Have a fresh activity and a test email
        Act: POST signup request
        Assert: Response should contain confirmation message
        """
        # Arrange
        activity_name = "Art Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, sample_email):
        """
        Arrange: Have an activity and a new email
        Act: POST signup request
        Assert: Email should be added to participants list
        """
        # Arrange
        activity_name = "Programming Class"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert sample_email in participants


class TestSignupValidation:
    """Tests for signup validation and error cases"""
    
    def test_signup_missing_email_parameter(self, client):
        """
        Arrange: Have an activity and no email parameter
        Act: POST signup request without email
        Assert: Response status should be 422 (validation error)
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422
    
    def test_signup_invalid_activity_not_found(self, client, sample_email):
        """
        Arrange: Have an invalid activity name and valid email
        Act: POST signup request to non-existent activity
        Assert: Response status should be 404
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_invalid_activity_returns_correct_error_message(self, client, sample_email):
        """
        Arrange: Have an invalid activity name
        Act: POST signup request to non-existent activity
        Assert: Error message should mention activity not found
        """
        # Arrange
        invalid_activity = "Fake Activity"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert "Activity not found" in response.json()["detail"]


class TestSignupDuplicatePrevention:
    """Tests for duplicate signup prevention"""
    
    def test_signup_duplicate_email_rejected(self, client):
        """
        Arrange: Have an activity with an existing participant
        Act: POST signup request with email that already participated
        Assert: Response status should be 400 and error should mention duplicate
        """
        # Arrange
        activity_name = "Drama Society"
        existing_email = "isabella@mergington.edu"  # Already in Drama Society
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_same_email_multiple_times_fails(self, client, sample_email):
        """
        Arrange: Sign up an email once, then try to sign up again
        Act: POST signup request with same email twice
        Assert: Second attempt should fail with 400
        """
        # Arrange
        activity_name = "Science Club"
        
        # Act - first signup succeeds
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Act - second signup fails
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()


class TestSignupCapacityLimits:
    """Tests for activity capacity enforcement"""
    
    def test_signup_rejected_when_activity_full(self, client):
        """
        Arrange: Have an activity that is at max capacity (Swimming Club: 2 max, 2 current)
        Act: POST signup request to full activity
        Assert: Response status should be 400 and mention full activity
        """
        # Arrange
        activity_name = "Swimming Club"  # max_participants: 1, already has 2
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    
    def test_signup_allowed_when_space_available(self, client, sample_email):
        """
        Arrange: Have an activity with available space (Basketball Team: 15 max, 2 current)
        Act: POST signup request to activity with space
        Assert: Response status should be 200
        """
        # Arrange
        activity_name = "Basketball Team"  # Has plenty of space
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_signup_capacity_increases_participant_count(self, client):
        """
        Arrange: Have an activity with available space
        Act: Sign up multiple students and check participant count
        Assert: Participant count should increase with each signup
        """
        # Arrange
        activity_name = "Advanced Math Olympiad"  # 12 max, 2 current
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act & Assert - verify each signup increases count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        for i, email in enumerate(emails):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            
            # Verify count increased
            updated_response = client.get("/activities")
            updated_count = len(updated_response.json()[activity_name]["participants"])
            assert updated_count == initial_count + i + 1
