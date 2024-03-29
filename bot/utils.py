
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import re

def create_inline_markup(list):
    keyboard_markup_list = []
    for reply in list:
        if reply:
            keyboard_markup_list.append(
                [InlineKeyboardButton(reply, callback_data=reply)]
            )
    return InlineKeyboardMarkup(keyboard_markup_list)


def is_valid_price(price):
    pattern = r"^-?\d{0,10}(\.\d{0,2})?$"
    return bool(re.match(pattern, price))


def check_date_format(date_string):
    pattern = r"\b\d{1,2}\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b"
    return bool(re.fullmatch(pattern, date_string, re.IGNORECASE))


def check_month_format(month_string):
    pattern = r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$"
    return bool(re.fullmatch(pattern, month_string, re.IGNORECASE))


def sanitize_error_message(error_message):
    # Regular expression to match URLs
    url_pattern = r'https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,}'
    
    # Replace URLs with "<url here>"
    sanitized_message = re.sub(url_pattern, '<url here>', error_message)
    
    return sanitized_message