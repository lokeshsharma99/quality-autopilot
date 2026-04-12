Feature: Example Feature
  As a user
  I want to perform actions on the website
  So that I can verify the application functionality

  Scenario: Navigate to homepage
    Given I navigate to the homepage
    Then I should see the page title

  Scenario: Search for a product
    Given I navigate to the homepage
    When I search for "laptop"
    Then I should see search results
