Feature: Admin User Management
  As an System Administrator
  I want to create and manage system users
  So that new employees can access the platform with designated roles

  Background:
    Given the user is logged in as an Admin

  @TC-05 @TC-06
  Scenario: Create a new system user, search list, and validate login
    # Step 1: Create New User
    When the user navigates to Admin > User Management > Users
    And clicks the Add button
    And fills in the new user details:
      | User Role    | ESS              |
      | Employee Name| Nithya S         |
      | Status       | Enabled          |
      | Username     | nithyasn         |
      | Password     | Password@123     |
    And clicks the Save button
    Then a success toast message "Successfully Saved" should appear

    # Step 2: Search user in Admin list (TC-06)
    When the user searches for the newly created username in the User Management list
    Then the user should be displayed in the results table

    # Step 3: Validate new user login (TC-05)
    When the user logs out of the application
    And logs in with the newly created user credentials
    Then the user should be logged in successfully
    And the top bar should display the user profile name