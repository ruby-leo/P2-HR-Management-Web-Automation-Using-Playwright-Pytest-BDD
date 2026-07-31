Feature: Leave Assignment and Tracking
  As an HR Administrator
  I want to assign leave to employees
  So that employee attendance and time off are accurately tracked

  Background:
    Given the user is logged into OrangeHRM as an Admin

  @TC-09
  Scenario: Assign leave to an employee and verify assignment
    When the Admin user navigates to Leave > Assign Leave
    And fills out the leave assignment form:
      | Employee Name | nithya s            |
      | Leave Type    | CAN - Personal      |
      | From Date     | 06-08-2026          |
      | To Date       | 06-08-2026          |
    And clicks the "Assign" button
    Then a confirmation toast message "Successfully Saved" should be displayed
    When the employee user navigates to Leave and then My Leave
    Then the newly assigned leave record should appear