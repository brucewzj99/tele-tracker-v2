# Release Notes
## Version 2.4.2 - Date 14 May 2024
### Bug Fix 🛠️
- Fix bug for backlog entry when backlog date doesn't exist

### For Developer 🧑‍💻
- Added new dev_testfunction to quickly test and debug functions

## Version 2.4.1.2 - Date 12 May 2024
### Bug Fix 🛠️
- Error handling for `/notifyall` command
- Add users count for `/notifyall` command

### For Developer 🧑‍💻
- Logging of error info message

## Version 2.4.1 - Date 12 May 2024
### Enhancement 🔥
- Added google form for reporting bugs, feedbacks and feature requests

## Version 2.4 - Date 6 May 2024
### Enhancement 🔥
- Clearer error messages for users

### For Developer 🧑‍💻
- Added more test case

## Version 2.3.7 - Date 3 May 2024
### For Developer 🧑‍💻
- Add number of error users for /notifyall command

## Version 2.3.6 - Date 3 May 2024
### For Developer 🧑‍💻
- Fix parse mode for /notifyall command

## Version 2.3.5 - Date 3 May 2024
### For Developer 🧑‍💻
- Add parse html for /notifyall command to send message with html tags

## Version 2.3.4 - Date 3 May 2024
### Enhancement 🔥
- Added FAQ section

### For Developer 🧑‍💻
- Add accessed time and usage count to database for tracking purposes
- Rename `test_` prefix to `dev_` for developer testing
- Remove old firestore codes, use new database module
- Added test for database module

## Version 2.3.3 - Date 1 May 2024
### Bug Fix 🛠️
- Add datetime and username for logging purposes
- Add more message to help command

## Version 2.3.2 - Date 27 Mar 2024
### Bug Fix 🛠️
- Fix backlog new date entry bug

## Version 2.3.1 - Date 18 Mar 2024
### Bug Fix 🛠️
- Censor URL for error message
- Month capitalize bug fix

## Version 2.3.0 - Date 16 Mar 2024
### For Developer 🧑‍💻
- Create new database module which is currently in use for future maintenance and development purposes

### Bug Fix 🛠️
- Censor URL for error message

## Version 2.2.1 - Date 24 Feb 2024
### Bug Fix 🛠️
- Include error message when replying back to users

## Version 2.2.0 - Date 27 Jan 2024
### Bug Fix 🛠️
- Fix backlog bug

## Version 2.1.9 - Date 23 Dec 2023
### For Developer 🧑‍💻
- Push features message to all users using `/notifyall` command (requires your telegram id)

## Version 2.1.8 - Date 17 Dec 2023
### Bug Fix 🛠️
- Fix add entry bug

## Version 2.1.7 - Date 16 Dec 2023
### New Features 🆕
- You can now add backdated transactions with `/backlog` command! 🎉

## Version 2.1.6 - Date 16 Dec 2023
### Bug Fix 🛠️
- Fix empty subcategory and subpayment bug

### New Features 🆕
- Added a new shortcode to retrieve transaction for today

### For Developer 🧑‍💻
- Mini refactor of code, added utils folder to store helper functions
- Added a new test_polling.py file to test polling locally
- Rename test.py to test_webhook.py for webhook testing

## Version 2.1.5 - Date 30 July 2023
### Bug Fix 🛠️
- Added tracker check when adding google sheet to prevent resetting of (existing) tracker

## Version 2.1.4 - Date 16 July 2023
### Bug Fix 🛠️
- Added end conversation handler for get day transaction

## Version 2.1.3 - Date 16 July 2023
### Enhancement 🔥
- Allows user to add multiple settings for quick transport
   - If there is only one settings, that will be used as default (/addtransport only)
- Revamp Google Sheet with new looks

### Bug Fix 🛠️
- Skip empty cells for payment & category

### For Developer 🧑‍💻
- Remove firebase codes

## Version 2.1.2 - Date 26 Jun 2023
### Bug Fix 🛠️
- When new users join, new date entry was not created
- Quick add settings not sending proper error message when either transport or others has been configured

## Version 2.1.1 - Date 8 Jun 2023
### Enhancement 🔥
- Migrate to use firestore
- Reformatted get overall transaction

## Version 2.1.0 - Date 1 Jun 2023
### New Features 🆕
- Added get overall functions

### Enhancement 🔥
- Rename retrievetransaction to getdaytransaction

### For Developer 🧑‍💻
- When you run test.py, ngrok will auto setup with the correct webhook!

## Version 2.0.2 - Date 1 Jun 2023
### Bug Fix 🛠️
- Day 1 sum creation bug

## Version 2.0.1 - Date 1 Jun 2023
### Bug Fix 🛠️
- Fix month abbreviation
- Fix updating of previous month

### For Developer 🧑‍💻
- Added a new updates.py file to push updates to all users
- To run updates, call functions in push_updates.py

## Version 2.0.0 - Date 28 May 2023
### Enhancement 🔥
- Cloud hosting w Flask & Vercel 🎉
- Move string to text_str.py

### Bug Fix 🛠️
- Allow negative price entry

### To note ❗
- Remove sql functions
- python-telegram-bot library changed to 13.7
- Move services account to environment variable
- Please read the new README for developer

## Version 1.2.0 - Date: 24 May 2023
### New Features 🆕 (Planned deployment: 27 May 2023)
- Retrieve past transaction with /retrievetransaction command
- Add income with /addincome command

### Enhancement 🔥
- Increase number of options for add others

## Version 1.1.0 - Date: 21 May 2023
### New Features 🆕
- Back button
- Added help command

### Bug Fixes 🛠️
- Remove 'Transport' category from others
- Fixed others and transport row tracker
- Fixed first row tracker

### Enhancement 🔥
- Refactor file structure

## Version 1.0.0 - Date: 20 May 2023
- Initial Launch