# Expense Module Test Cases

| TC ID   | Test Scenario                     | Steps                        | Expected Result              |
| ------- | --------------------------------- | ---------------------------- | ---------------------------- |
| EXP-001 | Add valid expense                 | Enter amount, category, date | Expense saved                |
| EXP-002 | Add expense with zero amount      | Amount = 0                   | Validation error             |
| EXP-003 | Add expense with negative amount  | Amount < 0                   | Validation error             |
| EXP-004 | Add expense without category      | Leave category blank         | Validation error             |
| EXP-005 | Add expense without note          | Leave note empty             | Expense still added          |
| EXP-006 | Edit existing expense             | Update amount/category       | Changes saved                |
| EXP-007 | Delete expense                    | Delete existing expense      | Expense removed              |
| EXP-008 | Expense appears in dashboard      | Add expense                  | Dashboard totals update      |
| EXP-009 | Expense filter 3 months           | Select `3m` filter           | Correct data shown           |
| EXP-010 | Expense filter 6 months           | Select `6m` filter           | Correct data shown           |
| EXP-011 | Expense filter 1 year             | Select `1y` filter           | Correct data shown           |
| EXP-012 | Custom date filter                | Select from/to dates         | Only matching expenses shown |
| EXP-013 | Future date expense               | Add future expense date      | Saved correctly              |
| EXP-014 | Expense JSON API                  | Open `/expenses/data`        | Valid JSON returned          |
| EXP-015 | Invalid expense edit ID           | Edit non-existing expense    | 404 error                    |
| EXP-016 | Missing CSRF while adding expense | Submit without token         | 400 error                    |


# Goal Management Test Cases
| TC ID    | Test Scenario                   | Steps                        | Expected Result              |
| -------- | ------------------------------- | ---------------------------- | ---------------------------- |
| GOAL-001 | Create valid goal               | Fill all required fields     | Goal created                 |
| GOAL-002 | Create goal with zero target    | Target = 0                   | Validation error             |
| GOAL-003 | Create goal with initial amount | Set current_amount > 0       | Goal expense auto-created    |
| GOAL-004 | Goal auto-completion            | Contribution reaches target  | Status becomes completed     |
| GOAL-005 | Add contribution                | Add valid contribution       | Amount updated               |
| GOAL-006 | Add zero contribution           | Amount = 0                   | Validation error             |
| GOAL-007 | Add negative contribution       | Amount < 0                   | Validation error             |
| GOAL-008 | Edit goal details               | Update target or name        | Goal updated                 |
| GOAL-009 | Edit with add_contribution      | Add contribution during edit | Expense auto-logged          |
| GOAL-010 | Delete goal                     | Delete existing goal         | Goal removed                 |
| GOAL-011 | Goal percentage calculation     | Update current amount        | Progress updates correctly   |
| GOAL-012 | Goal ETA calculation            | Add monthly contribution     | Months to goal calculated    |
| GOAL-013 | Zero monthly contribution       | Contribution = 0             | ETA shows “—”                |
| GOAL-014 | Goal category auto-create       | First contribution made      | “Goals” category created     |
| GOAL-015 | Goal appears in analytics       | Create goal                  | Analytics includes Goals row |
| GOAL-016 | Goals JSON API                  | Open `/goals/data`           | Valid JSON returned          |


# Dashboard Test Cases
| TC ID    | Test Scenario                 | Steps                    | Expected Result                        |
| -------- | ----------------------------- | ------------------------ | -------------------------------------- |
| DASH-001 | Dashboard loads correctly     | Login and open dashboard | Summary cards visible                  |
| DASH-002 | Zero budget handling          | Monthly budget = 0       | Budget percentage = 0, no crash        |
| DASH-003 | Money score calculation       | Add expenses and goals   | Score updates correctly                |
| DASH-004 | Recent expenses display       | Add 5+ expenses          | Latest 5 shown                         |
| DASH-005 | Budget allocation percentages | Add savings/invest goals | Correct percentages shown              |
| DASH-006 | Remaining budget calculation  | Budget > expenses        | Remaining amount correct               |
| DASH-007 | Negative remaining budget     | Expenses > budget        | Negative remaining displayed correctly |

# Analytics Test Cases
| TC ID   | Test Scenario             | Steps                         | Expected Result             |
| ------- | ------------------------- | ----------------------------- | --------------------------- |
| ANA-001 | Analytics page load       | Open analytics page           | Charts load                 |
| ANA-002 | Spending vs savings chart | Open API endpoint             | Correct JSON returned       |
| ANA-003 | 7-day range analytics     | Use `7d`                      | Daily labels shown          |
| ANA-004 | 30-day range analytics    | Use `30d`                     | Daily data returned         |
| ANA-005 | 6-month range analytics   | Use `6m`                      | Monthly labels shown        |
| ANA-006 | 1-year range analytics    | Use `1y`                      | Monthly data returned       |
| ANA-007 | Negative savings scenario | Spend beyond budget           | Savings goes negative       |
| ANA-008 | Category percentages      | Add multiple categories       | Percentages total 100       |
| ANA-009 | Fixed cost projection     | Add recurring expenses        | Monthly equivalents correct |
| ANA-010 | AI insights endpoint      | Open `/analytics/ai-insights` | JSON response returned      |
| ANA-011 | No expenses analytics     | User has no expenses          | Empty state handled         |
| ANA-012 | Goal analytics totals     | Add active goals              | Totals calculated correctly |


# Settings Test Cases
| TC ID   | Test Scenario                | Steps                     | Expected Result                    |
| ------- | ---------------------------- | ------------------------- | ---------------------------------- |
| SET-001 | Update profile settings      | Change name/currency      | Changes saved                      |
| SET-002 | Update monthly budget        | Enter budget amount       | Dashboard updates                  |
| SET-003 | Toggle AI alerts             | Enable/disable checkbox   | Setting saved                      |
| SET-004 | Toggle notifications         | Enable/disable checkbox   | Setting saved                      |
| SET-005 | Add recurring expense        | Fill valid fields         | Fixed cost added                   |
| SET-006 | Add yearly recurring expense | Billing cycle = yearly    | Monthly equivalent calculated      |
| SET-007 | Add weekly recurring expense | Billing cycle = weekly    | Monthly equivalent = amount × 4.33 |
| SET-008 | Delete recurring expense     | Delete fixed cost         | Removed successfully               |
| SET-009 | Tab persistence              | Open `?tab=fixed-costs`   | Correct tab active                 |
| SET-010 | Settings auto-create         | User missing settings row | New row auto-created               |


# Security And Validation Test Cases
| TC ID   | Test Scenario                    | Steps                          | Expected Result    |
| ------- | -------------------------------- | ------------------------------ | ------------------ |
| SEC-001 | Access protected page logged out | Open `/expenses/`              | Redirect to login  |
| SEC-002 | Cross-user expense edit          | Edit another user's expense    | 404 returned       |
| SEC-003 | Cross-user goal delete           | Delete another user's goal     | 404 returned       |
| SEC-004 | Missing CSRF token               | Submit POST without token      | 400 error          |
| SEC-005 | SQL injection in login           | Use SQL payload in email field | Login blocked      |
| SEC-006 | XSS in note field                | Add `<script>` in note         | Script escaped     |
| SEC-007 | Invalid category ID              | Submit fake category ID        | Validation failure |
| SEC-008 | Session timeout                  | Expire session manually        | Redirect to login  |
| SEC-009 | Invalid route access             | Open invalid endpoint          | 404 page shown     |


# API Validation Test Cases
| TC ID   | Endpoint                      | Validation                           |
| ------- | ----------------------------- | ------------------------------------ |
| API-001 | `/expenses/data`              | Returns authenticated user data only |
| API-002 | `/goals/data`                 | Proper goal serialization            |
| API-003 | `/analytics/spending-savings` | Correct JSON schema                  |
| API-004 | Invalid range query           | Graceful fallback                    |
| API-005 | Unauthorized API access       | Redirect or unauthorized             |
| API-006 | Empty dataset response        | Valid empty JSON arrays              |
| API-007 | Date formatting in APIs       | Matches spec                         |
| API-008 | Currency consistency          | User currency reflected              |

# High Priority Edge Cases
| TC ID    | Test Scenario                  | Steps                        | Expected Result               |
| -------- | ------------------------------ | ---------------------------- | ----------------------------- |
| EDGE-001 | Extremely large expense amount | Add ₹99999999                | Saved correctly               |
| EDGE-002 | Decimal amount precision       | Add ₹1234.56                 | Stored accurately             |
| EDGE-003 | No expenses this month         | Login with empty data        | Dashboard handles gracefully  |
| EDGE-004 | Multiple goals completed       | Complete all goals           | Analytics updates properly    |
| EDGE-005 | Deleted Goals category         | Remove from DB manually      | Recreated on contribution     |
| EDGE-006 | Budget lower than fixed costs  | Add large recurring expenses | Dashboard still calculates    |
| EDGE-007 | Empty analytics data           | New user account             | Empty graphs handled          |
| EDGE-008 | Invalid custom date range      | From > To                    | Validation error              |
| EDGE-009 | Leap year date expense         | Add Feb 29 entry             | Saved correctly               |
| EDGE-010 | Unicode note input             | Add emoji/local language     | Stored and displayed properly |


# Authentication Test Cases
| TC ID    | Test Scenario                  | Steps                                               | Expected Result                                 |
| -------- | ------------------------------ | --------------------------------------------------- | ----------------------------------------------- |
| AUTH-001 | Register with valid details    | Enter valid name, email, password, confirm password | User account created and redirected to settings |
| AUTH-002 | Register with existing email   | Use already registered email                        | Error message shown                             |
| AUTH-003 | Register with short password   | Enter password < 6 chars                            | Validation error                                |
| AUTH-004 | Password mismatch              | Password ≠ confirm password                         | Validation error                                |
| AUTH-005 | Login with valid credentials   | Enter correct email/password                        | Login success                                   |
| AUTH-006 | Login with invalid password    | Enter wrong password                                | Invalid credentials message                     |
| AUTH-007 | Logout                         | Click logout                                        | Session cleared and redirected                  |
| AUTH-008 | Remember me login              | Check remember me and login                         | Session persists after browser restart          |
| AUTH-009 | Access dashboard without login | Open `/` while logged out                           | Redirect to login page                          |
| AUTH-010 | Missing CSRF token on login    | Submit form without token                           | 400 error                                       |
