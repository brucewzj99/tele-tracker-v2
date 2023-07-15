# Release Notes

## Version 1.0.0 - Date: 20 May 2023
- Initial Launch

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

## Version 1.2.0 - Date: 24 May 2023
### New Features 🆕 (Planned deployment: 27 May 2023)
- Retrieve past transaction with /retrievetransaction command
- Add income with /addincome command

### Enhancement 🔥
- Increase number of options for add others

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

## Version 2.0.1 - Date 1 Jun 2023
### Bug Fix 🛠️
- Fix month abbreviation
- Fix updating of previous month

### For Developer 🧑‍💻
- Added a new updates.py file to push updates to all users
- To run updates, call functions in push_updates.py

## Version 2.0.2 - Date 1 Jun 2023
### Bug Fix 🛠️
- Day 1 sum creation bug

## Version 2.1.0 - Date 1 Jun 2023
### New Features 🆕
- Added get overall functions

### Enhancement 🔥
- Rename retrievetransaction to getdaytransaction

### For Developer 🧑‍💻
- When you run test.py, ngrok will auto setup with the correct webhook!


## Version 2.1.1 - Date 8 Jun 2023
### Enhancement 🔥
- Migrate to use firestore
- Reformatted get overall transaction

## Version 2.1.2 - Date 26 Jun 2023
### Bug Fix 🛠️
- When new users join, new date entry was not created
- Quick add settings not sending proper error message when either transport or others has been configured


## Version 2.1.3 - Date 16 July 2023
### Enhancement 🔥
- Allows user to add multiple settings for quick transport
   - If there is only one settings, that will be used as default (/addtransport only)
- Revamp Google Sheet with new looks

### Bug Fix 🛠️
- Skip empty cells for payment & category

### For Developer 🧑‍💻
- Remove firebase codes


## Version 2.1.4 - Date 16 July 2023
### Bug Fix 🛠️
- Added end conversation handler for get day transaction