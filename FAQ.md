## FAQ on TeleFinance Tracker Bot

### 1. Sometimes the bot doesn't reply when I enter data. What should I do?
The bot may occasionally encounter issues due to hosting limitations. If it doesn't respond, try waiting, or use `/cancel` and re-enter the data. Most of the time, `/cancel` would solve majority of your issues!

### 2. My entry ends up in the wrong category. How do I fix this?
When keying new entry, do ensure that you have received the "Transaction logged." message before adding a new one. For your current incorrect entries, you can manually adjust them in the Google Sheet.

### 3. How do I add past transactions or entries for previous months?
For entries from past months, you can manually add them directly to the Google Sheet. For transactions earlier in the current month, use the `/backlog` command.

### 4. How do I delete or edit a past entry?
To delete or edit past entries, manually adjust them in the Google Sheet. Remember not to shift the remaining entries up, as this could disrupt new entries.

### 5. Can I add or edit quick settings for `/quickothers` or `/quicktransport`?
Yes, you can customize these settings by modifying the tracker tab in the Google Sheet. There is a limit set in the bot to prevent excessively long lists.

### 6. How do I view all the commands available?
You can view all available commands by opening the menu in the Telegram chat or by typing `/help`.

### 7. I edited the Google Sheet, but the bot doesn't seem to recognize the changes. What should I do?
Do ensure that `TRACKER` under the Tracker tab is correctly updated. The first row refers to the row number the first entry is on, the Transport Row and Other Row should refers to the last entry of the respective category. This means there's possiblity that the Other or Transport Row is -1 of first row.

![tracker fixed](https://github.com/brucewzj99/tele-tracker-v2/doc-image/faq-tracker.png)


### If you have additional questions or need further assistance, feel free to [open a new issue](https://github.com/brucewzj99/tele-tracker-v2/issues) on GitHub.