Feature: Navigation and Menu Validation
  As an authenticated user
  I want to see and access all relevant navigation menus
  So that I can easily move across different modules

  Background:
    Given the user is logged into OrangeHRM with valid credentials

  @TC-04
  Scenario: Verify side navigation menu items
    Then the side navigation panel should display the following items:
      | Admin      |
      | PIM        |
      | Leave      |
      | Time       |
      | Recruitment|
      | My Info    |
      | Performance|
      | Dashboard  |
      | Directory  |
      | Maintenance|
      | Claim      |
      | Buzz       |
    And each menu item should be visible and clickable

  @TC-08
  Scenario: Validate presence and accessibility of sub-menu items under My Info
    When the user navigates to the My Info section
    Then the following sub-tabs should be visible and accessible:
      | Personal Details   |
      | Contact Details    |
      | Emergency Contacts |
      | Dependents         |
      | Immigration        |
      | Job                |
      | Salary             |
      | Qualifications     |
      | Memberships        |
    And clicking each sub-tab should navigate to its corresponding details page