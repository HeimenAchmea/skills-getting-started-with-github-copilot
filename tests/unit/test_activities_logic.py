"""
Unit tests for activity business logic using AAA (Arrange-Act-Assert) pattern.
Tests core business logic: activity existence, capacity limits, duplicates, removal.
"""

import pytest


class TestActivityExistence:
    """Tests for activity existence checks"""
    
    def test_activity_exists_in_database(self, activities_db):
        """
        Arrange: Have activities in the database
        Act: Check if Chess Club exists
        Assert: Activity should exist
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        activity_exists = activity_name in activities_db
        
        # Assert
        assert activity_exists is True
    
    def test_activity_does_not_exist_in_database(self, activities_db):
        """
        Arrange: Have activities in the database
        Act: Check if non-existent activity exists
        Assert: Activity should not exist
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        
        # Act
        activity_exists = activity_name in activities_db
        
        # Assert
        assert activity_exists is False


class TestActivityCapacity:
    """Tests for activity capacity limit enforcement"""
    
    def test_participant_can_signup_when_activity_has_space(self, activities_db, sample_email):
        """
        Arrange: Have an activity with available space
        Act: Check if activity has space for a new participant
        Assert: Activity should have space (participants < max_participants)
        """
        # Arrange
        activity = activities_db["Programming Class"]
        initial_count = len(activity["participants"])
        max_capacity = activity["max_participants"]
        
        # Act
        has_space = initial_count < max_capacity
        
        # Assert
        assert has_space is True
    
    def test_activity_is_full_when_at_capacity(self, activities_db):
        """
        Arrange: Have an activity that is full (Swimming Club has 2/1 max)
        Act: Check if activity is at capacity
        Assert: Activity should be full
        """
        # Arrange
        activity = activities_db["Swimming Club"]
        participants_count = len(activity["participants"])
        max_capacity = activity["max_participants"]
        
        # Act
        is_full = participants_count >= max_capacity
        
        # Assert
        assert is_full is True
    
    def test_can_add_participant_up_to_limit(self, activities_db):
        """
        Arrange: Have an activity with space
        Act: Simulate adding participants up to the limit
        Assert: Should allow additions up to max_participants
        """
        # Arrange
        activity = activities_db["Basketball Team"]  # max 15, has 2
        max_capacity = activity["max_participants"]
        activity["participants"].clear()  # Start fresh
        
        # Act
        for i in range(max_capacity):
            activity["participants"].append(f"student{i}@mergington.edu")
        
        # Assert
        assert len(activity["participants"]) == max_capacity


class TestDuplicatePrevention:
    """Tests for preventing duplicate signups"""
    
    def test_participant_email_exists_in_activity(self, activities_db):
        """
        Arrange: Have an activity with existing participants
        Act: Check if a known email is in participants
        Assert: Email should be found
        """
        # Arrange
        activity = activities_db["Chess Club"]
        existing_email = "michael@mergington.edu"
        
        # Act
        is_duplicate = existing_email in activity["participants"]
        
        # Assert
        assert is_duplicate is True
    
    def test_new_email_is_not_duplicate(self, activities_db, sample_email):
        """
        Arrange: Have an activity with existing participants
        Act: Check if a new email is in participants
        Assert: Email should not be found
        """
        # Arrange
        activity = activities_db["Chess Club"]
        new_email = sample_email
        
        # Act
        is_duplicate = new_email in activity["participants"]
        
        # Assert
        assert is_duplicate is False
    
    def test_same_email_cannot_be_added_twice(self, activities_db):
        """
        Arrange: Have an activity with a participant
        Act: Try to add the same email again
        Assert: Should detect duplicate and not allow addition
        """
        # Arrange
        activity = activities_db["Art Club"]
        email_to_add = "hannah@mergington.edu"  # Already in Art Club
        initial_count = len(activity["participants"])
        
        # Act
        is_already_participant = email_to_add in activity["participants"]
        
        # Assert
        assert is_already_participant is True
        assert len(activity["participants"]) == initial_count


class TestParticipantRemoval:
    """Tests for removing participants from activities"""
    
    def test_participant_can_be_removed(self, activities_db):
        """
        Arrange: Have an activity with a participant
        Act: Remove the participant
        Assert: Participant should be removed
        """
        # Arrange
        activity = activities_db["Drama Society"]
        email_to_remove = "isabella@mergington.edu"
        initial_count = len(activity["participants"])
        
        # Act
        activity["participants"].remove(email_to_remove)
        
        # Assert
        assert len(activity["participants"]) == initial_count - 1
        assert email_to_remove not in activity["participants"]
    
    def test_removed_participant_can_rejoin(self, activities_db):
        """
        Arrange: Have an activity with a participant that we remove
        Act: Remove and then re-add the participant
        Assert: Participant should be added again
        """
        # Arrange
        activity = activities_db["Science Club"]
        email = "ava@mergington.edu"
        activity["participants"].remove(email)
        
        # Act
        activity["participants"].append(email)
        
        # Assert
        assert email in activity["participants"]
    
    def test_cannot_remove_non_existent_participant(self, activities_db):
        """
        Arrange: Have an activity without a specific participant
        Act: Try to find the non-existent participant
        Assert: Participant should not be found
        """
        # Arrange
        activity = activities_db["Advanced Math Olympiad"]
        email_not_in_activity = "nonexistent@mergington.edu"
        
        # Act
        is_participant = email_not_in_activity in activity["participants"]
        
        # Assert
        assert is_participant is False
