# Tele-Tracker Bot
A python telegram bot to help track daily expenses onto google sheet, hosted on Vercel using Flask.

[Version 1](https://github.com/brucewzj99/tele-tracker) was hosted locally with a different version of python-telegram-bot

## Release Notes
You can find the release notes over [here](https://github.com/brucewzj99/tele-tracker-v2/blob/master/release_notes.md).

## Table of Contents
- [Getting Started (Users)](#getting-started-users)
- [Getting Started (Developers)](#getting-started-developers)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Getting Started (Users)
1. Access the bot on [telegram](https://t.me/telefinance_tracker_bot) 
2. Use the /start command and follow the instructions given.
3. Remember to edit the `Dropdown` sheet on [Google Sheet](https://docs.google.com/spreadsheets/d/1-XVdaeq1qqnLqAttGGzki6NkavqpkKs1n6Elz4GDC2I/edit#gid=612397734) to get started.
![image](https://github.com/brucewzj99/tele-tracker-v2/assets/24997286/c6411808-3740-4454-aada-cd3ff4d8b6f4)

4. Happy using!

## Getting Started (Developers)
### Step 1
* Fork the repo and run the code below to installed the required dependencies
``` python
pip install -r requirements.txt
```
* Install [ngrok](https://ngrok.com/download) 

### Step 2
* Go to Google Cloud Platform
* Set up Google Sheet API, download service account key
* Retrieve Google Sheet API email
* Set up Firebase Firestore Database, download service account key
* Retrieve your firebase database url
* Set up telegram bot via [BotFather](https://t.me/BotFather)
* Insert all of them into .env as follows, you can use py dotenv or set it as env variable in your venv
* You can use the same TOKEN for BOT_TOKEN & TEST_TOKEN but I recommend using two different bots for testing and production

``` .env
BOT_TOKEN=your_bot_token
TEST_TOKEN=your_test_token
DATABASE_URL=firebase_url
GOOGLE_API_EMAIL=google_api_email
FIREBASE_JSON=service_account_key
GOOGLE_JSON=service_account_key
MASTER_TELE_ID=your_telegram_id
```

### Step 3
* Proceed to project directory and run:
``` python
python3.9 test.py
```

## Usage
/start - Initialize and Configure Sheet

/config - Update Sheet Settings

/addentry - Add Expense Entry

/addtransport - Quick Add Transport Entry

/addothers - Quick Add Other Entry

/addincome - Add Income Entry

/backlog - Add backdated transaction

/getdaytransaction - Retrieve transaction from dates

/getoverall - Retrieve overall transaction for a month

/cancel - Cancel Conversation

/help - Show Help

/notifyall - Send message to all users (requires your telegram id/only for admin)

## Contributing
If you want to contribute or have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue or work on issues that are currently open.
Don't forget to give the project a ⭐! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Bruce Wang: hello@brucewzj.com

LinkedIn: [https://www.linkedin.com/in/brucewzj/](https://www.linkedin.com/in/brucewzj/)

Project Link: [https://github.com/brucewzj99/tele-tracker-v2](https://github.com/brucewzj99/tele-tracker-v2)
