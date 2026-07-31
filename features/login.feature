Feature: OrangeHRM Login and Authentication
  As a user of OrangeHRM
  I want to access the login page and authenticate
  So that I can securely manage HR activities

  Background:
    Given the user launches the browser

  @TC-02
  Scenario: Verify OrangeHRM URL accessibility
    When the user navigates to login page
    Then the login page should load successfully without errors

  @TC-03
  Scenario: Validate presence and state of login input fields
    When the user navigates to the OrangeHRM login page
    Then the "Username" input field should be visible and enabled
    And the "Password" input field should be visible and enabled

  @TC-01
  Scenario Outline: Validate login functionality with multiple sets of credentials
    Given the user is on the OrangeHRM login page
    When the user enters username "<username>" and password "<password>"
    And clicks the Login button
    Then the login outcome should be "<expected_result>"
    And an appropriate message "<message>" should be displayed if rejected

    Examples:
      | username       | password | expected_result | message             |
      | Admin          | admin123 | Success         | Dashboard           |
      | Random Input   | admin123 | Failure         | Invalid credentials |
      | Admin          | wrong123 | Failure         | Invalid credentials |
      |                | admin123 | Failure         | Required            |
      | Admin          |          | Failure         | Required            |

  @TC-07
  Scenario: Verify "Forgot Password" functionality
    Given the user is on the OrangeHRM login page
    When the user clicks on the "Forgot your password?" link
    Then the user should be redirected to the Reset Password page
    When the user enters username "JC1234"
    And clicks the "Reset Password" button
    Then a confirmation message Reset Password link sent successfully should appear