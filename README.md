# Tele-Tracker Bot
A python telegram bot to help track daily expenses onto google sheet

## Release Notes
You can find the release notes over [here](https://github.com/brucewzj99/tele-tracker/blob/master/release_notes.md)

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
3. Remember to edit the `Dropdown` sheet on Google Sheet to get started.
![image](https://github.com/brucewzj99/tele-tracker-v2/assets/24997286/664b6e2e-5c56-47b2-b56b-a5b3424bf7bd)
4. Happy using!

## Getting Started (Developers)
### Step 1
* Fork the repo and run the code below to installed the required dependencies
```python
pip install -r requirements.txt
```
* Install [ngrok](https://ngrok.com/download) 

### Step 2
* Go to Google Cloud Platform
* Set up Google Sheet API, download service account key
* Retrieve Google Sheet API email
* Set up Firebase Realtime Database, download service account key
* Retrieve your firebase database url
* Set up telegram bot via [BotFather](https://t.me/BotFather)
* Insert all of them into .env as follows
```.env
BOT_TOKEN=your_bot_token
DATABASE_URL=firebase_url
GOOGLE_API_EMAIL=google_api_email
FIREBASE_JSON=service_account_key
GOOGLE_JSON=service_account_key
```

### Step 3
* Run ngrok
```terminal
ngrok http 5000
```
* Copy the link, it should look something like this 'https://<address>.ap.ngrok.io'
* Set up web hook by opening this link:
```url
https://api.telegram.org/bot<bot_token>/setwebhook?url=https://<address>.ap.ngrok.io/webhook
```
* You should see this:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```
* Proceed to project directory and run:
```python
python3.9 test.py
```

## Usage
/start - Start the bot and configure your Google Sheet for tracking expenses and other entries.

/config - Update your Google Sheet settings or configure quick settings for adding transport and other entries.

/addentry - Add a new entry to your expense tracking system.

/addtransport - Quickly add a new transport entry to your expense tracker.

/addothers - Quickly add another type of entry to your expense tracker.

/addincome - Add a new entry to your income.

/retrievetransaction - Retrieve a transaction from past date.

/cancel - Cancel the previous conversation with the bot and start fresh.

/help - Show help message

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue or work on issues that are currently open.
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE.txt` for more information.

## Contact
Bruce Wang: hello@brucewzj.com

LinkedIn: [https://www.linkedin.com/in/brucewzj/](https://www.linkedin.com/in/brucewzj/)

Project Link: [https://github.com/brucewzj99/tele-tracker](https://github.com/brucewzj99/tele-tracker)
