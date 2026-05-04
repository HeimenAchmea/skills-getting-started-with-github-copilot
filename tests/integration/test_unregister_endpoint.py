"""
Integration tests for DELETE /activities/{activity_name}/unregister endpoint using AAA pattern.
Tests unregistration functionality with success cases, validation, and error scenarios.
"""

import pytest


class TestUnregisterSuccessful:
    """Tests for successful unregister scenarios"""
    
    def test_unregister_successful_removes_participant(self, client):
        """
        Arrange: Have an activity with a registered participant
        Act: DELETE unregister request with valid activity and email
        Assert: Response status should be 200 and participant should be removed
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_unregister = "michael@mergington.edu"  # Already in Chess Club
        
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity_name]["participants"])
        assert email_to_unregister in initial_response.json()[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_unregister}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_participants = len(updated_response.json()[activity_name]["participants"])
        assert updated_participants == initial_participants - 1
        assert email_to_unregister not in updated_response.json()[activity_name]["participants"]
    
    def test_unregister_response_contains_confirmation_message(self, client):
        """
        Arrange: Have an activity with a registered participant
        Act: DELETE unregister request
        Assert: Response should contain confirmation message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_unregister_removes_from_participants_list(self, client):
        """
        Arrange: Have an activity with a registered participant
        Act: DELETE unregister request
        Assert: Email should be removed from participants list
        """
        # Arrange
        activity_name = "Art Club"
        email = "hannah@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email not in participants
    
    def test_unregister_allows_signup_again(self, client):
        """
        Arrange: Have a registered participant
        Act: Unregister and then sign up again
        Assert: Should be able to sign up again successfully
        """
        # Arrange
        activity_name = "Drama Society"
        email = "isabella@mergington.edu"
        
        # Act - unregister
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act - sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200


class TestUnregisterValidation:
    """Tests for unregister validation and error cases"""
    
    def test_unregister_missing_email_parameter(self, client):
        """
        Arrange: Have an activity and no email parameter
        Act: DELETE unregister request without email
        Assert: Response status should be 422 (validation error)
        """
        # Arrange
        activity_name = "Science Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        # Assert
        assert response.status_code == 422
    
    def test_unregister_invalid_activity_not_found(self, client):
        """
        Arrange: Have an invalid activity name and valid email
        Act: DELETE unregister request to non-existent activity
        Assert: Response status should be 404
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_invalid_activity_returns_correct_error_message(self, client):
        """
        Arrange: Have an invalid activity name
        Act: DELETE unregister request to non-existent activity
        Assert: Error message should mention activity not found
        """
        # Arrange
        invalid_activity = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterNonParticipant:
    """Tests for preventing unregister of non-participants"""
    
    def test_unregister_student_not_in_activity_fails(self, client):
        """
        Arrange: Have an activity and an email not in that activity
        Act: DELETE unregister request with non-participant email
        Assert: Response status should be 400 and error should mention not registered
        """
        # Arrange
        activity_name = "Advanced Math Olympiad"
        non_participant_email = "notparticipant@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": non_participant_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_twice_fails_on_second_attempt(self, client):
        """
        Arrange: Have a registered participant
        Act: Unregister twice
        Assert: Second unregister should fail with 400
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        # Act - first unregister succeeds
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Act - second unregister fails
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response2.status_code == 400
        assert "not registered" in response2.json()["detail"].lower()
    
    def test_unregister_student_from_wrong_activity_fails(self, client):
        """
        Arrange: Have a student in Activity A, try to unregister from Activity B
        Act: DELETE unregister from activity without participant
        Assert: Should return 400 error
        """
        # Arrange
        # michael@mergington.edu is in Chess Club but not in Basketball Team
        activity_name = "Basketball Team"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()


class TestUnregisterCapacity:
    """Tests for capacity behavior after unregister"""
    
    def test_unregister_opens_space_for_new_signup(self, client):
        """
        Arrange: Have a full activity, unregister a participant
        Act: Unregister one participant and then sign up a new one
        Assert: New signup should succeed
        """
        # Arrange
        activity_name = "Gym Class"  # max 2, has 2 (at capacity)
        email_to_remove = "john@mergington.edu"
        new_email = "newstudent@mergington.edu"
        
        # Verify it's full first
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        assert initial_count >= 2  # At capacity
        
        # Act - unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        assert response1.status_code == 200
        
        # Act - sign up new student
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response2.status_code == 200
    
    def test_unregister_decreases_participant_count(self, client):
        """
        Arrange: Have an activity with multiple participants
        Act: Unregister multiple students and verify count decreases
        Assert: Participant count should decrease with each unregister
        """
        # Arrange
        activity_name = "Drama Society"
        emails_to_remove = ["isabella@mergington.edu", "mason@mergington.edu"]
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act & Assert - verify count decreases
        for i, email in enumerate(emails_to_remove):
            response = client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
            
            updated_response = client.get("/activities")
            updated_count = len(updated_response.json()[activity_name]["participants"])
            assert updated_count == initial_count - (i + 1)
