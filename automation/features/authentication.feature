Feature: User Authentication
  As a user of the Universal Credit application
  I want to authenticate with my credentials
  So that I can access the protected areas of the application

  Background:
    Given the user is on the login page

  Scenario: Successful login with valid credentials
    When the user logs in with valid credentials
    Then the user should be redirected to the dashboard
    And the user should see a welcome message

  Scenario: Login with invalid credentials
    When the user attempts to login with invalid credentials
    Then an error message should be displayed
    And the user should remain on the login page

  Scenario: Logout
    Given the user is logged in
    When the user logs out
    Then the user should be redirected to the login page

  Scenario: Access to protected page without authentication
    When the user attempts to access a protected page directly
    Then the user should be redirected to the login page