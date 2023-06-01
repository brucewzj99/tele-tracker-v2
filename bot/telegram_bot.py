import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)
import re
import pytz
import datetime as dt
from warnings import filterwarnings

from bot.text_str import *
from bot.common import EntryType
from bot.common import ConversationState as CS
import bot.google_sheet as gs
import bot.firebase as db

timezone = pytz.timezone("Asia/Singapore")


def create_inline_markup(list):
    keyboard_markup_list = []
    for reply in list:
        keyboard_markup_list.append([InlineKeyboardButton(reply, callback_data=reply)])
    return InlineKeyboardMarkup(keyboard_markup_list)


def is_valid_price(price):
    pattern = r"^-?\d{0,10}(\.\d{0,2})?$"
    return bool(re.match(pattern, price))


def check_date_format(date_string):
    pattern = r"\b\d{1,2}\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b"
    return bool(re.fullmatch(pattern, date_string, re.IGNORECASE))


def get_category_text(sheet_id, entry_type):
    msg = ""
    markup_list = []
    if entry_type == EntryType.TRANSPORT:
        msg = DEFAULT_TRANSPORT_TEXT
        markup_list = gs.get_main_dropdown_value(sheet_id, EntryType.TRANSPORT)
    elif entry_type == EntryType.OTHERS:
        msg = DEFAULT_CATEGORY_TEXT
        markup_list = gs.get_main_dropdown_value(sheet_id, EntryType.OTHERS)
    return msg, markup_list


def get_payment_text(sheet_id):
    payment_list = gs.get_main_dropdown_value(sheet_id, "Payment")
    return payment_list


def start(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    try:
        user_exists = db.check_if_user_exists(telegram_id)
        if user_exists:
            context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id)
            link = f"https://docs.google.com/spreadsheets/d/{context.user_data['sheet_id']}/edit"
            update.message.reply_text(
                f"Seems like you have already linked a Google sheet with us, do you want to link a different Google sheet with us?\n\n{link}",
                reply_markup=create_inline_markup(["Yes", "No"]),
            )
            return CS.RESET_UP
        else:
            update.message.reply_text(SETUP_TEXT)
            return CS.SET_UP
    except Exception as e:
        update.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def set_up(update, context) -> int:
    telegram_id = update.effective_user.id
    url = update.message.text

    pattern = r"/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, url)
    if match:
        sheet_id = match.group(1)
        try:
            db.new_user_setup(telegram_id, sheet_id)
            current_datetime = dt.datetime.now(timezone)
            day = current_datetime.day
            gs.update_rows(sheet_id, day, 4, 5)  # New users start from row 5
            update.message.reply_text(SUCCESS_LINK_TEXT)
            return ConversationHandler.END
        except Exception as e:
            update.message.reply_text(GSHEET_ERROR_TEXT)
            return ConversationHandler.END
    else:
        update.message.reply_text(GSHEET_WRONG_TEXT)
        return CS.SET_UP


def reset_up(update, context) -> int:
    reply = update.callback_query.data
    update.callback_query.answer()
    if reply == "Yes":
        update.callback_query.message.reply_text(SETUP_TEXT)
        return CS.SET_UP
    else:
        update.callback_query.edit_message_text(END_TEXT, reply_markup=None)
        return ConversationHandler.END


def config(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id)
    list = [
        "Change Google Sheet",
        "Configure Quick Transport",
        "Configure Quick Others",
        "Cancel",
    ]
    update.message.reply_text(
        "How can i help you today?", reply_markup=create_inline_markup(list)
    )
    return CS.CONFIG_HANDLER


def config_handler(update, context) -> int:
    reply = update.callback_query.data
    update.callback_query.answer()
    if reply == "Cancel":
        update.callback_query.edit_message_text(END_TEXT, reply_markup=None)
        return ConversationHandler.END
    update.callback_query.edit_message_text(reply, reply_markup=None)
    if reply == "Change Google Sheet":
        update.callback_query.message.reply_text(SETUP_TEXT)
        return CS.SET_UP
    else:
        try:
            if reply == "Configure Quick Transport":
                context.user_data["config"] = EntryType.TRANSPORT
                msg = f"This is your current Transport settings.\n"
                setting_list = gs.get_quick_add_settings(
                    context.user_data["sheet_id"], context.user_data["config"]
                )
                # Retrieve current settings
                if setting_list == None:
                    msg = f"{msg}Default Payment: None\nDefault Type: None\n"
                else:
                    msg = f"{msg}Default Payment: {setting_list[0]}\nDefault Type: {setting_list[1]}\n"
                msg = f"{msg}Do you want to update it?"
                update.callback_query.message.reply_text(
                    msg, reply_markup=create_inline_markup(["Yes", "No"])
                )
                return CS.CONFIG_SETUP
            elif reply == "Configure Quick Others":
                context.user_data["config"] = EntryType.OTHERS
                msg = QUICK_OTHER_TEXT
                setting_list = gs.get_quick_add_others(context.user_data["sheet_id"])
                keyboard_list = []
                if setting_list == None:
                    msg = f"{msg}No settings found\n"
                else:
                    for setting in setting_list:
                        msg = f"{msg}{setting}\n"
                if len(setting_list) < QUICK_OTHER_LIMIT:
                    keyboard_list.append("Add new")
                keyboard_list.append("Cancel")
                update.callback_query.message.reply_text(
                    msg, reply_markup=create_inline_markup(keyboard_list)
                )
                return CS.CONFIG_SETUP
        except Exception as e:
            update.callback_query.message.reply_text(ERROR_TEXT)
            return ConversationHandler.END


def config_setup(update, context) -> int:
    reply = update.callback_query.data
    update.callback_query.answer()
    config = context.user_data["config"]
    try:
        if reply == "Yes" or reply == "Add new":
            markup_list = gs.get_main_dropdown_value(
                context.user_data["sheet_id"], config
            )
            update.callback_query.message.edit_text(
                f"Choose your default {config.value} type.",
                reply_markup=create_inline_markup(markup_list),
            )
            return CS.CONFIG_CATEGORY
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END
    update.callback_query.edit_message_text(END_TEXT, reply_markup=None)
    return ConversationHandler.END


def config_category(update, context) -> int:
    reply = update.callback_query.data
    update.callback_query.answer()
    config = context.user_data["config"]
    context.user_data["config-category"] = reply
    try:
        sheet_id = context.user_data["sheet_id"]
        update.callback_query.answer()
        if config == EntryType.TRANSPORT:
            update.callback_query.edit_message_text(
                f"Default transport type: {reply}", reply_markup=None
            )
            payment_list = gs.get_main_dropdown_value(sheet_id, "Payment")
            update.callback_query.message.reply_text(
                DEFAULT_PAYMENT_TEXT, reply_markup=create_inline_markup(payment_list)
            )
            return CS.CONFIG_PAYMENT
        elif config == EntryType.OTHERS:
            sub_markup_list = gs.get_sub_dropdown_value(sheet_id, reply, config)
            if len(sub_markup_list) > 1:
                sub_markup_list.pop(0)
                update.callback_query.message.edit_text(
                    DEFAULT_SUBCATEGORY_TEXT,
                    reply_markup=create_inline_markup(sub_markup_list),
                )
                return CS.CONFIG_SUBCATEGORY
    except Exception as e:
        update.callback_query.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def config_subcategory(update, context) -> int:
    reply = update.callback_query.data
    context.user_data[
        "config-category"
    ] = f'{context.user_data["config-category"]} - {reply}'
    try:
        sheet_id = context.user_data["sheet_id"]
        payment_list = gs.get_main_dropdown_value(sheet_id, "Payment")
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            f'Default category type: {context.user_data["config-category"]}',
            reply_markup=None,
        )
        update.callback_query.message.reply_text(
            DEFAULT_PAYMENT_TEXT, reply_markup=create_inline_markup(payment_list)
        )
        return CS.CONFIG_PAYMENT
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def config_payment(update, context) -> int:
    reply = update.callback_query.data
    try:
        sheet_id = context.user_data["sheet_id"]
        update.callback_query.answer()
        context.user_data["config-payment"] = reply
        sub_markup_list = gs.get_sub_dropdown_value(sheet_id, reply, "Payment")
        if len(sub_markup_list) > 1:
            sub_markup_list.pop(0)
            update.callback_query.message.edit_text(
                DEFAULT_PAYMENT_TEXT, reply_markup=create_inline_markup(sub_markup_list)
            )
            return CS.CONFIG_SUBPAYMENT
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def config_subpayment(update, context) -> int:
    reply = update.callback_query.data
    context.user_data[
        "config-payment"
    ] = f'{context.user_data["config-payment"]} - {reply}'
    try:
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            f'Payment type: {context.user_data["config-payment"]}', reply_markup=None
        )
        gs.update_quick_add_settings(
            context.user_data["sheet_id"],
            context.user_data["config"],
            context.user_data["config-payment"],
            context.user_data["config-category"],
        )
        update.callback_query.message.reply_text(
            f'Default {context.user_data["config"].value} settings updated.'
        )
        return ConversationHandler.END
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def add_entry(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id)
    update.message.reply_text(
        ENTRY_TYPE_TEXT,
        reply_markup=create_inline_markup(
            [entry_type.value for entry_type in EntryType]
        ),
    )
    return CS.ENTRY


def entry(update, context) -> int:
    reply = update.callback_query.data
    context.user_data["entry_type"] = EntryType[reply.upper()]
    update.callback_query.answer()
    update.callback_query.edit_message_text(f"Entry type: {reply}", reply_markup=None)
    update.callback_query.message.reply_text(PRICE_DEFAULT_TEXT)
    return CS.PRICE


def price(update, context) -> int:
    reply = update.message.text
    if is_valid_price(reply):
        context.user_data["price"] = reply
        entry_type = context.user_data["entry_type"]
        if entry_type == EntryType.TRANSPORT:
            update.message.reply_text(TRANSPORT_DEFAULT_TEXT)
        elif entry_type == EntryType.OTHERS:
            update.message.reply_text(REMARKS_DEFAULT_TEXT)
        return CS.REMARKS
    else:
        update.message.reply_text(PRICE_RETRY_TEXT)
        return CS.PRICE


def remarks(update: Update, context) -> int:
    reply = update.message.text
    context.user_data["remarks"] = reply
    entry_type = context.user_data["entry_type"]
    sheet_id = context.user_data["sheet_id"]

    # Check if is there is only one comma for start and end destination
    if entry_type == EntryType.TRANSPORT:
        if reply.count(",") != 1:
            update.message.reply_text(TRANSPORT_DEFAULT_TEXT)
            return CS.REMARKS
    msg, markup_list = get_category_text(sheet_id, entry_type)
    try:
        update.message.reply_text(msg, reply_markup=create_inline_markup(markup_list))
        return CS.CATEGORY
    except Exception as e:
        update.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def category(update, context) -> int:
    reply = update.callback_query.data
    entry_type = context.user_data["entry_type"]
    try:
        sheet_id = context.user_data["sheet_id"]
        update.callback_query.answer()
        if entry_type == EntryType.TRANSPORT:
            update.callback_query.edit_message_text(
                f"Transport type: {reply}", reply_markup=None
            )
            context.user_data["category"] = f"{reply}"
            payment_list = get_payment_text(sheet_id)
            update.callback_query.message.reply_text(
                DEFAULT_PAYMENT_TEXT, reply_markup=create_inline_markup(payment_list)
            )
            return CS.PAYMENT
        elif entry_type == EntryType.OTHERS:
            context.user_data["category"] = reply
            sub_markup_list = gs.get_sub_dropdown_value(sheet_id, reply, entry_type)
            if len(sub_markup_list) > 1:
                sub_markup_list.pop(0)
                sub_markup_list.append(BACK_TEXT)
                update.callback_query.message.edit_text(
                    DEFAULT_SUBCATEGORY_TEXT,
                    reply_markup=create_inline_markup(sub_markup_list),
                )
                return CS.SUBCATEGORY
            # This won't be called as there will always be a subcategory, but just in case
            else:
                update.callback_query.edit_message_text(
                    f"Category type: {reply}", reply_markup=None
                )
                return CS.PAYMENT
    except Exception as e:
        update.callback_query.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def subcategory(update, context) -> int:
    reply = update.callback_query.data
    sheet_id = context.user_data["sheet_id"]
    entry_type = context.user_data["entry_type"]
    update.callback_query.answer()
    if reply == BACK_TEXT:
        msg, markup_list = get_category_text(sheet_id, entry_type)
        update.callback_query.edit_message_text(
            msg, reply_markup=create_inline_markup(markup_list)
        )
        return CS.CATEGORY
    try:
        context.user_data["category"] = f'{context.user_data["category"]} - {reply}'
        update.callback_query.edit_message_text(
            f'Category type: {context.user_data["category"]}', reply_markup=None
        )
        payment_list = get_payment_text(sheet_id)
        update.callback_query.message.reply_text(
            DEFAULT_PAYMENT_TEXT, reply_markup=create_inline_markup(payment_list)
        )
        return CS.PAYMENT
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def payment(update, context) -> int:
    reply = update.callback_query.data
    try:
        sheet_id = context.user_data["sheet_id"]
        update.callback_query.answer()
        context.user_data["payment"] = reply
        sub_markup_list = gs.get_sub_dropdown_value(sheet_id, reply, "Payment")
        if len(sub_markup_list) > 1:
            sub_markup_list.pop(0)
            sub_markup_list.append(BACK_TEXT)
            update.callback_query.message.edit_text(
                DEFAULT_PAYMENT_TEXT, reply_markup=create_inline_markup(sub_markup_list)
            )
            return CS.SUBPAYMENT
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def subpayment(update, context) -> int:
    reply = update.callback_query.data
    update.callback_query.answer()
    sheet_id = context.user_data["sheet_id"]
    if reply == BACK_TEXT:
        payment_list = get_payment_text(sheet_id)
        update.callback_query.edit_message_text(
            DEFAULT_PAYMENT_TEXT, reply_markup=create_inline_markup(payment_list)
        )
        return CS.PAYMENT
    try:
        context.user_data["payment"] = f'{context.user_data["payment"]} - {reply}'
        update.callback_query.edit_message_text(
            f'Payment type: {context.user_data["payment"]}', reply_markup=None
        )
        log_transaction(context.user_data, update)
        update.callback_query.message.reply_text("Transaction logged.")
        return ConversationHandler.END

    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def log_transaction(user_data, update):
    sheet_id = user_data["sheet_id"]
    trackers = gs.get_trackers(sheet_id)

    # datatime data
    current_datetime = dt.datetime.now(timezone)
    day = current_datetime.day
    month = current_datetime.strftime("%B")

    # tracker data
    day_tracker = int(trackers[0])
    other_row_tracker = int(trackers[1])
    transport_row_tracker = int(trackers[2])
    first_row = int(trackers[3])

    # user input data
    entry_type = user_data["entry_type"]
    payment = user_data["payment"]
    price = user_data["price"]
    category = user_data["category"]
    remarks = user_data["remarks"]
    row_data = [entry_type, price, remarks, category, payment]

    msg = ""
    # start new date if date elapsed
    if day_tracker < day or day == 1:
        msg = f"New entry for {day} {month}"
        if day == 1:
            month = (current_datetime - dt.timedelta(days=1)).strftime("%B")
        # update prev day
        msg = f"{msg}\nCreating sum for day {day_tracker}"
        gs.update_prev_day(sheet_id, month, first_row)
        if day == 1:
            new_row = 5
            first_row = 6
            gs.update_rows(sheet_id, 1, new_row, first_row)
        else:
            new_row = gs.get_new_row(sheet_id, month)
            first_row = new_row + 1
            gs.update_rows(sheet_id, day, new_row, first_row)
        if update.callback_query and update.callback_query.message:
            update.callback_query.message.reply_text(msg)
        elif update.message:
            update.message.reply_text(msg)

        transport_row_tracker = new_row
        first_row = new_row + 1
        other_row_tracker = new_row
        # enter date into cell
        gs.create_date(sheet_id, day, month, first_row)

    # update row + 1
    gs.row_incremental(sheet_id, entry_type)
    if entry_type == EntryType.TRANSPORT:
        transport_row_tracker += 1
    else:
        other_row_tracker += 1
    # create entry
    if entry_type == EntryType.TRANSPORT:
        gs.create_entry(sheet_id, month, transport_row_tracker, row_data)
    else:
        gs.create_entry(sheet_id, month, other_row_tracker, row_data)


def cancel(update, context):
    update.message.reply_text(END_TEXT, reply_markup=None)
    return ConversationHandler.END


def add_transport(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id)
        context.user_data["entry_type"] = EntryType.TRANSPORT
        setting_list = gs.get_quick_add_settings(
            context.user_data["sheet_id"], EntryType.TRANSPORT
        )
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END
    if setting_list is None or setting_list[0] is None:
        update.message.reply_text(QUICK_SETUP_TRANSPORT)
        return ConversationHandler.END
    else:
        context.user_data["payment"] = setting_list[0]
        context.user_data["category"] = setting_list[1]
        update.message.reply_text(
            f"Quick Add Transport\nDefault Payment: {setting_list[0]}\nDefault Type: {setting_list[1]}"
            + "\n\nPlease enter as follow: [price],[start],[end]\n e.g. 2.11, Home, Work"
        )
    return CS.QUICK_ADD


def add_others(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id)
        context.user_data["entry_type"] = EntryType.OTHERS
        setting_list = gs.get_quick_add_settings(
            context.user_data["sheet_id"], EntryType.OTHERS
        )
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END
    if setting_list is None or setting_list[0] is None:
        update.message.reply_text(QUICK_SETUP_OTHER)
        return ConversationHandler.END
    else:
        setting_list = gs.get_quick_add_others(context.user_data["sheet_id"])
        update.message.reply_text(
            "Quick Add Others, please choose your category.",
            reply_markup=create_inline_markup(setting_list),
        )
    return CS.QUICK_ADD_CATEGORY


def quick_add_category(update, context) -> int:
    reply = update.callback_query.data
    context.user_data["payment"], context.user_data["category"] = reply.split(",")
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        f'Quick Add Others\nDefault Payment: {context.user_data["payment"]}\nDefault Type: {context.user_data["category"]}'
        + "\n\nPlease enter as follow: [price],[remarks]\n e.g. 19.99, New shirt",
        reply_markup=None,
    )
    return CS.QUICK_ADD


def quick_add(update, context) -> int:
    reply = update.message.text
    try:
        context.user_data["price"], context.user_data["remarks"] = reply.split(",", 1)
        try:
            log_transaction(context.user_data, update)
            update.message.reply_text("Transaction logged.")
            return ConversationHandler.END
        except Exception as e:
            update.message.reply_text(ERROR_TEXT)
            return ConversationHandler.END
    except Exception as e:
        update.message.reply_text("Please follow the format and try again.")
        return CS.QUICK_ADD


def help(update, context):
    update.message.reply_text(HELP_TEXT)


def retrieve_transaction(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id)
        update.message.reply_text(RETRIEVE_TRANSACTION_TEXT)
        return CS.HANDLE_RETRIEVE_TRANSACTION
    except Exception as e:
        update.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def handle_retrieve_transaction(update, context):
    sheet_id = context.user_data["sheet_id"]
    reply = update.message.text
    msg = ""
    try:
        if check_date_format(reply):
            day, month = reply.split(" ")
            total_spend, transport_values, other_values = gs.retrieve_transaction(
                sheet_id, month, day
            )
            if not total_spend:
                total_spend = "To be determine"
            else:
                total_spend = total_spend[0][0]
            msg = f"Transaction for {day} {month}\nTotal Spending: {total_spend}\n----TRANSPORT----\n"
            for transport in transport_values:
                msg = f"{msg}{transport}\n"
            msg = f"{msg}\n----OTHERS----\n"
            for other in other_values:
                msg = f"{msg}{other}\n"
            update.message.reply_text(msg)
            return ConversationHandler.END
        else:
            update.message.reply_text(RETRIEVE_TRANSACTION_TEXT)
            return CS.HANDLE_RETRIEVE_TRANSACTION
    except Exception as e:
        update.message.reply_text(ERROR_TEXT)


def add_income(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id)
        update.message.reply_text(ADD_INCOME_TEXT)
    except Exception as e:
        update.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END
    return CS.INCOME


def income(update, context) -> int:
    reply = update.message.text
    income = ""
    remarks = ""
    if "," in reply:
        income, remarks = reply.split(",")
    else:
        if is_valid_price(income):
            income = reply
        else:
            update.message.reply_text(ADD_INCOME_RETRY_TEXT)
            return CS.INCOME
    context.user_data["income"] = income.strip()
    context.user_data["remarks"] = remarks.strip()
    try:
        sheet_id = context.user_data["sheet_id"]
        work_list = gs.get_work_place(sheet_id)
        update.message.reply_text(
            CHOOSE_INCOME_SOURCE_TEXT, reply_markup=create_inline_markup(work_list)
        )
        return CS.WORK_PLACE
    except Exception as e:
        update.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def work_place(update, context) -> int:
    place = update.callback_query.data
    context.user_data["place"] = place
    update.callback_query.answer()
    update.callback_query.message.edit_text(f"Place: {place}", reply_markup=None)
    update.callback_query.message.reply_text(
        CPF_TEXT, reply_markup=create_inline_markup(["Yes", "No"])
    )
    return CS.CPF


def cpf(update, context) -> int:
    cpf = update.callback_query.data
    income = context.user_data["income"]
    remarks = context.user_data["remarks"]
    place = context.user_data["place"]
    sheet_id = context.user_data["sheet_id"]
    update.callback_query.answer()
    update.callback_query.message.edit_text(f"CPF: {cpf}", reply_markup=None)
    try:
        row_data = [income, place, cpf, remarks]
        current_datetime = dt.datetime.now(timezone)
        month = current_datetime.strftime("%B")
        if gs.update_income(sheet_id, month, row_data):
            update.callback_query.message.reply_text("Income has been added!")
        else:
            update.callback_query.message.reply_text(INCOME_LIMIT_TEXT)
        return ConversationHandler.END
    except Exception as e:
        update.callback_query.message.reply_text(ERROR_TEXT)
        return ConversationHandler.END


def setup_handlers(dispatcher):
    # Configuration-related states and handlers
    config_states = {
        CS.CONFIG_HANDLER: [CallbackQueryHandler(config_handler)],
        CS.CONFIG_SETUP: [CallbackQueryHandler(config_setup)],
        CS.CONFIG_CATEGORY: [CallbackQueryHandler(config_category)],
        CS.CONFIG_SUBCATEGORY: [CallbackQueryHandler(config_subcategory)],
        CS.CONFIG_PAYMENT: [CallbackQueryHandler(config_payment)],
        CS.CONFIG_SUBPAYMENT: [CallbackQueryHandler(config_subpayment)],
    }

    # Entry-related states and handlers
    entry_states = {
        CS.ENTRY: [CallbackQueryHandler(entry)],
        CS.PRICE: [MessageHandler(Filters.text & ~Filters.command, price)],
        CS.REMARKS: [MessageHandler(Filters.text & ~Filters.command, remarks)],
        CS.CATEGORY: [CallbackQueryHandler(category)],
        CS.SUBCATEGORY: [CallbackQueryHandler(subcategory)],
        CS.PAYMENT: [CallbackQueryHandler(payment)],
        CS.SUBPAYMENT: [CallbackQueryHandler(subpayment)],
    }

    # Quick add-related states and handlers
    quick_add_states = {
        CS.QUICK_ADD: [MessageHandler(Filters.text & ~Filters.command, quick_add)],
        CS.QUICK_ADD_CATEGORY: [CallbackQueryHandler(quick_add_category)],
    }

    # Retrieve transaction-related states and handlers
    retrieve_transaction_states = {
        CS.HANDLE_RETRIEVE_TRANSACTION: [
            MessageHandler(Filters.text & ~Filters.command, handle_retrieve_transaction)
        ],
    }

    add_income_states = {
        CS.INCOME: [MessageHandler(Filters.text & ~Filters.command, income)],
        CS.WORK_PLACE: [CallbackQueryHandler(work_place)],
        CS.CPF: [CallbackQueryHandler(cpf)],
    }
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("config", config),
            CommandHandler("addentry", add_entry),
            CommandHandler("addtransport", add_transport),
            CommandHandler("addothers", add_others),
            CommandHandler("addincome", add_income),
            CommandHandler("retrievetransaction", retrieve_transaction),
        ],
        states={
            CS.SET_UP: [MessageHandler(Filters.text & ~Filters.command, set_up)],
            CS.RESET_UP: [CallbackQueryHandler(reset_up)],
            **config_states,
            **entry_states,
            **quick_add_states,
            **retrieve_transaction_states,
            **add_income_states,
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)

    help_handler = CommandHandler("help", help)
    dispatcher.add_handler(help_handler)
