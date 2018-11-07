# mint budget
An automated personal budgeting solution using Mint and Google Docs

## Required docs not included in the github repo
* services/client_secret_gspread.json - key to access google docs
* services/secrets.py - contains dictionary called 'login' with 'username' and 'password' items for mint login
* services/budget_xwalks.py - contains crosswalks determined needed from mint data

## TODO

Logging, error handling, tests - add more!
Auto create new spreadsheet tabs when in new month
iPhone notification
Temporary transactions with flag
Delete old temp transactions each day
Email two factor authentication and automate response 

Message should include:
Summary:
Cash balance - Credit card balance = net cash
Total budgeted expenses - actual expenses = remaining
Restaurants and groceries remaining budget
All budget line items over budget

Details:
List and category of new transactions
List of uncategorized transactions
Total and count of amazon needing categorization
"# py-budget" 
