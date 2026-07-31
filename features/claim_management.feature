Feature: Employee Expense Claims
  As an employee
  I want to initiate expense claim requests
  So that I can get reimbursed for official expenses

  Background:
    Given the user is logged in as an employee

  @TC-10
  Scenario: Initiate and submit a new expense claim request
    When the user navigates to the Claim section
    And clicks on Submit Claim
    And selects Event Accommodation and Currency and enter reason
    And clicks "Create"
    Then a success confirmation message should be displayed
    When the user checks the "My Claims" history table
    Then the newly submitted claim should be listed with status Initiated