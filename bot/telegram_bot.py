import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
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
import bot.google_sheet_service as gs
from bot.database_service import firestore_service
import bot.utils as utils

from bot.error_handler import TelegramBotError, GoogleSheetError, DatabaseError

db = firestore_service.FirestoreService()
timezone = pytz.timezone("Asia/Singapore")
MASTER_TELE_ID = os.environ.get("MASTER_TELE_ID")


def get_category_text(sheet_id, entry_type):
    msg = ""
    markup_list = []
    try:
        if entry_type == EntryType.TRANSPORT:
            msg = DEFAULT_TRANSPORT_TEXT
            markup_list = gs.get_main_dropdown_value(sheet_id, EntryType.TRANSPORT)
        elif entry_type == EntryType.OTHERS:
            msg = DEFAULT_CATEGORY_TEXT
            markup_list = gs.get_main_dropdown_value(sheet_id, EntryType.OTHERS)
        return msg, markup_list
    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise TelegramBotError(message="Error getting category text", extra_info=str(e))


def get_payment_text(sheet_id):
    try:
        payment_list = gs.get_main_dropdown_value(sheet_id, "Payment")
        return payment_list
    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise TelegramBotError(message="Error getting payment text", extra_info=str(e))


def start(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        user_exists = db.check_if_user_exists(telegram_id)
        if user_exists:
            context.user_data["sheet_id"] = db.get_user_sheet_id(
                telegram_id, telegram_username
            )
            link = f"https://docs.google.com/spreadsheets/d/{context.user_data['sheet_id']}/edit"
            update.message.reply_text(
                f"Seems like you have already linked a Google sheet with us, do you want to link a different Google sheet with us?\n\n{link}",
                reply_markup=utils.create_inline_markup(["Yes", "No"]),
            )
            return CS.RESET_UP
        else:
            update.message.reply_text(SETUP_TEXT, parse_mode=ParseMode.HTML)
            return CS.SET_UP
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def set_up(update, context) -> int:
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    url = update.message.text

    pattern = r"/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, url)
    if match:
        sheet_id = match.group(1)
        try:
            db.new_user_setup(telegram_id, sheet_id, telegram_username)
            current_datetime = dt.datetime.now(timezone)
            day = current_datetime.day
            month = current_datetime.strftime("%b")

            # get tracker data to check if got input
            trackers = gs.get_trackers(sheet_id)
            if trackers:  # If got input
                day_tracker = int(trackers[0])
                first_row = int(trackers[3])
                if day_tracker == day:
                    pass
                elif day_tracker < day:
                    prev_month = (current_datetime - dt.timedelta(days=1)).strftime(
                        "%b"
                    )
                    gs.update_prev_day(sheet_id, prev_month, first_row)
                    new_row = gs.get_last_entered_row(sheet_id, month)
                    first_row = new_row + 1
                    gs.update_tracker_values(sheet_id, day, new_row, first_row)
                    gs.create_date(sheet_id, day, month, first_row)
                elif day == 1:
                    new_row = 4
                    first_row = 5
                    gs.update_tracker_values(sheet_id, day, new_row, first_row)
                    gs.create_date(sheet_id, day, month, first_row)
            else:  # New sheet
                new_row = 4
                first_row = 5
                gs.update_tracker_values(
                    sheet_id, day, new_row, first_row
                )  # New users start from row 5
            gs.create_date(sheet_id, day, month, first_row)
            update.message.reply_text(SUCCESS_LINK_TEXT)
        
        except GoogleSheetError as e:
            update.message.reply_text(
                ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
            )
        except DatabaseError as e:
            update.message.reply_text(
                ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
            )
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
        update.callback_query.message.reply_text(SETUP_TEXT, parse_mode=ParseMode.HTML)
        return CS.SET_UP
    else:
        update.callback_query.edit_message_text(END_TEXT, reply_markup=None)
        return ConversationHandler.END


def config(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id, telegram_username)
    list = [
        "Change Google Sheet",
        "Configure Quick Transport",
        "Configure Quick Others",
        "Cancel",
    ]
    update.message.reply_text(
        "How can i help you today?", reply_markup=utils.create_inline_markup(list)
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
        update.callback_query.message.reply_text(SETUP_TEXT, parse_mode=ParseMode.HTML)
        return CS.SET_UP
    else:
        try:
            if reply == "Configure Quick Transport":
                context.user_data["config"] = EntryType.TRANSPORT
                msg = QUICK_TRANSPORT_TEXT
                limit = QUICK_TRANSPORT_LIMIT
            elif reply == "Configure Quick Others":
                context.user_data["config"] = EntryType.OTHERS
                msg = QUICK_OTHER_TEXT
                limit = QUICK_OTHER_LIMIT

            setting_list = gs.get_quick_add_list(
                context.user_data["sheet_id"], context.user_data["config"]
            )
            keyboard_list = []
            if setting_list == None:
                msg = f"{msg}No settings found\n"
            else:
                for setting in setting_list:
                    msg = f"{msg}{setting}\n"
            if len(setting_list) < limit:
                keyboard_list.append("Add new")
            keyboard_list.append("Cancel")
            update.callback_query.message.reply_text(
                msg, reply_markup=utils.create_inline_markup(keyboard_list)
            )
            return CS.CONFIG_SETUP
        except Exception as e:
            update.callback_query.message.reply_text(
                ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
            )
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
                reply_markup=utils.create_inline_markup(markup_list),
            )
            return CS.CONFIG_CATEGORY
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
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
                DEFAULT_PAYMENT_TEXT,
                reply_markup=utils.create_inline_markup(payment_list),
            )
            return CS.CONFIG_PAYMENT
        elif config == EntryType.OTHERS:
            sub_markup_list = gs.get_sub_dropdown_value(sheet_id, reply, config)
            if len(sub_markup_list) > 1:
                sub_markup_list.pop(0)
                update.callback_query.message.edit_text(
                    DEFAULT_SUBCATEGORY_TEXT,
                    reply_markup=utils.create_inline_markup(sub_markup_list),
                )
                return CS.CONFIG_SUBCATEGORY
    except Exception as e:
        update.callback_query.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
        return ConversationHandler.END


def config_subcategory(update, context) -> int:
    reply = update.callback_query.data
    context.user_data["config-category"] = (
        f'{context.user_data["config-category"]} - {reply}'
    )
    try:
        sheet_id = context.user_data["sheet_id"]
        payment_list = gs.get_main_dropdown_value(sheet_id, "Payment")
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            f'Default category type: {context.user_data["config-category"]}',
            reply_markup=None,
        )
        update.callback_query.message.reply_text(
            DEFAULT_PAYMENT_TEXT, reply_markup=utils.create_inline_markup(payment_list)
        )
        return CS.CONFIG_PAYMENT    
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
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
                DEFAULT_PAYMENT_TEXT,
                reply_markup=utils.create_inline_markup(sub_markup_list),
            )
            return CS.CONFIG_SUBPAYMENT
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
        return ConversationHandler.END


def config_subpayment(update, context) -> int:
    reply = update.callback_query.data
    context.user_data["config-payment"] = (
        f'{context.user_data["config-payment"]} - {reply}'
    )
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
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
        return ConversationHandler.END


def add_entry(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id, telegram_username)
        update.message.reply_text(
            ENTRY_TYPE_TEXT,
            reply_markup=utils.create_inline_markup(
                [entry_type.value for entry_type in EntryType]
            ),
        )
        return CS.ENTRY
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
        return ConversationHandler.END


def entry(update, context) -> int:
    reply = update.callback_query.data
    context.user_data["entry_type"] = EntryType[reply.upper()]
    update.callback_query.answer()
    update.callback_query.edit_message_text(f"Entry type: {reply}", reply_markup=None)
    update.callback_query.message.reply_text(PRICE_DEFAULT_TEXT)
    return CS.PRICE


def price(update, context) -> int:
    reply = update.message.text
    if utils.is_valid_price(reply):
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
        
    try:
        msg, markup_list = get_category_text(sheet_id, entry_type)
        update.message.reply_text(
            msg, reply_markup=utils.create_inline_markup(markup_list)
        )
        return CS.CATEGORY
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
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
                DEFAULT_PAYMENT_TEXT,
                reply_markup=utils.create_inline_markup(payment_list),
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
                    reply_markup=utils.create_inline_markup(sub_markup_list),
                )
                return CS.SUBCATEGORY
            # This won't be called as there will always be a subcategory, but just in case
            else:
                update.callback_query.edit_message_text(
                    f"Category type: {reply}", reply_markup=None
                )
                payment_list = get_payment_text(sheet_id)
                update.callback_query.message.reply_text(
                    DEFAULT_PAYMENT_TEXT,
                    reply_markup=utils.create_inline_markup(payment_list),
                )
                return CS.PAYMENT
    except Exception as e:
        update.callback_query.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def subcategory(update, context) -> int:
    reply = update.callback_query.data
    sheet_id = context.user_data["sheet_id"]
    entry_type = context.user_data["entry_type"]
    update.callback_query.answer()
    try:
        if reply == BACK_TEXT:
            msg, markup_list = get_category_text(sheet_id, entry_type)
            update.callback_query.edit_message_text(
                msg, reply_markup=utils.create_inline_markup(markup_list)
            )
            return CS.CATEGORY
        context.user_data["category"] = f'{context.user_data["category"]} - {reply}'
        update.callback_query.edit_message_text(
            f'Category type: {context.user_data["category"]}', reply_markup=None
        )
        payment_list = get_payment_text(sheet_id)
        update.callback_query.message.reply_text(
            DEFAULT_PAYMENT_TEXT, reply_markup=utils.create_inline_markup(payment_list)
        )
        return CS.PAYMENT
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
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
                DEFAULT_PAYMENT_TEXT,
                reply_markup=utils.create_inline_markup(sub_markup_list),
            )
            return CS.SUBPAYMENT
        # This won't be called as there will always be a subpayment, but just in case
        else:
            update.callback_query.edit_message_text(
                f'Payment type: {context.user_data["payment"]}', reply_markup=None
            )
            if context.user_data.get("backlog"):
                backlog_transaction(context.user_data, update)
            else:
                log_transaction(context.user_data, update)
            update.callback_query.message.reply_text("Transaction logged.")
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def subpayment(update, context) -> int:
    reply = update.callback_query.data
    update.callback_query.answer()
    sheet_id = context.user_data["sheet_id"]
    
    try:
        if reply == BACK_TEXT:
            payment_list = get_payment_text(sheet_id)
            update.callback_query.edit_message_text(
                DEFAULT_PAYMENT_TEXT, reply_markup=utils.create_inline_markup(payment_list)
            )
            return CS.PAYMENT
        context.user_data["payment"] = f'{context.user_data["payment"]} - {reply}'
        update.callback_query.edit_message_text(
            f'Payment type: {context.user_data["payment"]}', reply_markup=None
        )
        if context.user_data.get("backlog"):
            backlog_transaction(context.user_data, update)
        else:
            log_transaction(context.user_data, update)
        update.callback_query.message.reply_text("Transaction logged.")
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def log_transaction(user_data, update):
    sheet_id = user_data["sheet_id"]
    trackers = gs.get_trackers(sheet_id)

    # datatime data
    current_datetime = dt.datetime.now(timezone)
    day = current_datetime.day
    month = current_datetime.strftime("%b")

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
    try:
        # start new date if date elapsed
        if day_tracker != day:
            msg = f"New entry for {day} {month}"
            prev_month = month
            # this should fix the bug regarding if first day of month not keyed in, but not tested
            if day == 1 | day < day_tracker:
                prev_month = (current_datetime - dt.timedelta(days=1)).strftime("%b")
            # update prev day
            msg = f"{msg}\nCreating sum for day {day_tracker}"
            gs.update_prev_day(sheet_id, prev_month, first_row)
            if day == 1 | day < day_tracker:
                new_row = 4
                first_row = 5
                gs.update_tracker_values(sheet_id, 1, new_row, first_row)
            else:
                new_row = gs.get_last_entered_row(sheet_id, month)
                first_row = new_row + 1
                gs.update_tracker_values(sheet_id, day, new_row, first_row)
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
    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise TelegramBotError(message="Error logging transaction", extra_info=str(e))


def backlog_transaction(user_data, update):
    sheet_id = user_data["sheet_id"]

    backlog_day = user_data["backlog_day"]
    backlog_month = user_data["backlog_month"]

    # datatime data
    current_datetime = dt.datetime.now(timezone)
    month = current_datetime.strftime("%b")

    try:
        # if backlog month is current month, need to move all one down
        if backlog_month.title() == month:
            gs.row_incremental_all(sheet_id)

        # user input data
        entry_type = user_data["entry_type"]
        payment = user_data["payment"]
        price = user_data["price"]
        category = user_data["category"]
        remarks = user_data["remarks"]
        row_data = [entry_type, price, remarks, category, payment]

        # create backlog entry
        gs.create_backlog_entry(sheet_id, backlog_day, backlog_month, row_data)
    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise TelegramBotError(message="Error logging backlog transaction", extra_info=str(e))


def cancel(update, context):
    update.message.reply_text(END_TEXT, reply_markup=None)
    context.user_data.clear()
    return ConversationHandler.END


def add_transport(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(
            telegram_id, telegram_username
        )
        context.user_data["entry_type"] = EntryType.TRANSPORT
        setting_list = gs.get_quick_add_settings(
            context.user_data["sheet_id"], EntryType.TRANSPORT
        )
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
        return ConversationHandler.END
    
    if not setting_list or not setting_list[0]:
        update.message.reply_text(QUICK_SETUP_TRANSPORT)
        return ConversationHandler.END
    else:
        try:
            setting_list = gs.get_quick_add_list(
                context.user_data["sheet_id"], context.user_data["entry_type"]
            )
            if len(setting_list) == 1:
                payment, category = setting_list[0].split(",")
                context.user_data["payment"] = payment
                context.user_data["category"] = category
                update.message.reply_text(
                    f"Quick Add Transport\nDefault Payment: {payment}\nDefault Type: {category}"
                    + "\n\nPlease enter as follow: [price],[start],[end]\n e.g. 2.11, Home, Work"
                )
                return CS.QUICK_ADD
            else:
                update.message.reply_text(
                    "Quick Add Transport, please choose your category.",
                    reply_markup=utils.create_inline_markup(setting_list),
                )
                return CS.QUICK_ADD_TRANSPORT
        except Exception as e:
            update.message.reply_text(
                ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
            )
        return ConversationHandler.END


def add_others(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(
            telegram_id, telegram_username
        )
        context.user_data["entry_type"] = EntryType.OTHERS
        setting_list = gs.get_quick_add_settings(
            context.user_data["sheet_id"], EntryType.OTHERS
        )
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
        return ConversationHandler.END
    
    if not setting_list or not setting_list[0]:
        update.message.reply_text(QUICK_SETUP_OTHER)
        return ConversationHandler.END
    else:
        try:
            setting_list = gs.get_quick_add_list(
                context.user_data["sheet_id"], context.user_data["entry_type"]
            )
            update.message.reply_text(
                "Quick Add Others, please choose your category.",
                reply_markup=utils.create_inline_markup(setting_list),
            )
        except Exception as e:
            update.message.reply_text(
                ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
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


def quick_add_transport(update, context) -> int:
    reply = update.callback_query.data
    context.user_data["payment"], context.user_data["category"] = reply.split(",")
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        f'Quick Add Transport\nDefault Payment: {context.user_data["payment"]}\nDefault Type: {context.user_data["category"]}'
        + "\n\nPlease enter as follow: [price],[start],[end]\n e.g. 2.11, Home, Work"
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
            update.message.reply_text(
                ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
            )
            return ConversationHandler.END
    except Exception as e:
        update.message.reply_text("Please follow the format and try again.")
        return CS.QUICK_ADD


def help(update, context):
    update.message.reply_text(HELP_TEXT)


def get_day_transaction(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(
            telegram_id, telegram_username
        )
        update.message.reply_text(GET_TRANSACTION_TEXT)
        return CS.HANDLE_GET_TRANSACTION
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
        return ConversationHandler.END


def get_overall(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(
            telegram_id, telegram_username
        )
        update.message.reply_text(GET_OVERALL_TEXT)
        return CS.HANDLE_GET_OVERALL
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def handle_get_transaction(update, context):
    sheet_id = context.user_data["sheet_id"]
    reply = update.message.text
    msg = ""
    try:
        if reply.lower() == "tdy":
            reply = dt.datetime.now(timezone).strftime("%d %b").lstrip("0")
        if utils.check_date_format(reply):
            day, month = reply.split(" ")
            total_spend, transport_values, other_values = gs.get_day_transaction(
                sheet_id, month, day
            )
            if (
                total_spend == None
                and transport_values == None
                and other_values == None
            ):
                update.message.reply_text(
                    f"No transaction found for {day} {month}", reply_markup=None
                )
                return ConversationHandler.END

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
            update.message.reply_text(GET_TRANSACTION_TEXT)
            return CS.HANDLE_GET_TRANSACTION
    except GoogleSheetError as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def handle_get_overall(update, context):
    sheet_id = context.user_data["sheet_id"]
    month = update.message.text
    try:
        if utils.check_month_format(month):
            values = gs.get_overall(sheet_id, month)

            final_income = values[0]
            msg = f"--- Final Income ---\n`{final_income[2]}`\n\n"

            msg += "--- Spending ---\n"
            max_len = (
                max(len(row[0]) for row in values[1:-2]) + 1
            )  # +1 for some extra space
            for row in values[1:-2]:
                if row[1].startswith("-"):  # if value is negative
                    msg += f"`{row[0].ljust(max_len)}{row[1]}`\n"
                else:
                    msg += f"`{row[0].ljust(max_len)} {row[1]}`\n"  # else keep the original space

            total_spent = values[-2]
            msg += f"\n--- Total Spent ---\n`{total_spent[1]}`\n"

            overall = values[-1]
            msg += f"\n--- Overall ---\n`{overall[2]}`\n"

            update.message.reply_text(msg, parse_mode="Markdown")
            return ConversationHandler.END
        else:
            update.message.reply_text(GET_OVERALL_TEXT)
            return CS.HANDLE_GET_OVERALL
    except GoogleSheetError as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def add_income(update, context):
    context.user_data.clear()
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(
            telegram_id, telegram_username
        )
        update.message.reply_text(ADD_INCOME_TEXT)
        return CS.INCOME
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def income(update, context) -> int:
    reply = update.message.text
    income = ""
    remarks = ""
    if "," in reply:
        income, remarks = reply.split(",")
    else:
        if utils.is_valid_price(income):
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
            CHOOSE_INCOME_SOURCE_TEXT,
            reply_markup=utils.create_inline_markup(work_list),
        )
        return CS.WORK_PLACE
    except Exception as e:
        update.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def work_place(update, context) -> int:
    place = update.callback_query.data
    context.user_data["place"] = place
    update.callback_query.answer()
    update.callback_query.message.edit_text(f"Place: {place}", reply_markup=None)
    update.callback_query.message.reply_text(
        CPF_TEXT, reply_markup=utils.create_inline_markup(["Yes", "No"])
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
        month = current_datetime.strftime("%b")
        if gs.update_income(sheet_id, month, row_data):
            update.callback_query.message.reply_text("Income has been added!")
        else:
            update.callback_query.message.reply_text(INCOME_LIMIT_TEXT)
    except Exception as e:
        update.callback_query.message.reply_text(
            ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
    return ConversationHandler.END


def backlog(update, context) -> int:
    context.user_data.clear()
    update.message.reply_text(BACKLOG_DATE_TEXT)
    context.user_data["backlog"] = True
    return CS.ADD_BACKLOG_ENTRY


def add_backlog_entry(update, context) -> int:
    reply = update.message.text
    if utils.check_date_format(reply):
        if reply == dt.datetime.now(timezone).strftime("%d %b").lstrip("0").lower():
            context.user_data["backlog"] = False
        else:
            day, month = reply.split(" ")
            context.user_data["backlog_day"] = day
            context.user_data["backlog_month"] = month
    else:
        update.message.reply_text(BACKLOG_DATE_TEXT)
        return CS.ADD_BACKLOG_ENTRY

    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username
    try:
        context.user_data["sheet_id"] = db.get_user_sheet_id(telegram_id, telegram_username)
        update.message.reply_text(
            ENTRY_TYPE_TEXT,
            reply_markup=utils.create_inline_markup(
                [entry_type.value for entry_type in EntryType]
            ),
        )
        return CS.ENTRY
    except DatabaseError as e:
        raise e
    except Exception as e:
        raise TelegramBotError(message="Error adding backlog entry", extra_info=str(e))    


def send_new_feature_message(context, new_feature_message):
    try:
        users = db.get_all_user_id()
        no_of_users = 0
        no_of_error_users = 0
        errors = []
        
        for user_id in users:
            try:
                context.bot.send_message(
                    chat_id=user_id,
                    text=new_feature_message,
                    parse_mode=ParseMode.HTML,
                )
                no_of_users += 1
            except Exception as e:
                try:
                    chat = context.bot.get_chat(chat_id=user_id)
                    username = chat.username if chat.username else "?"
                except Exception:
                    username = "?"
                no_of_error_users += 1
                errors.append(f"Username @{username} (ID: {user_id}): {e}")

        error_message = "\n".join(errors)
        return no_of_users, no_of_error_users, error_message
    except DatabaseError as e:
        raise e
    except Exception as e:
        raise TelegramBotError(message="Fail to send new feature message", extra_info=str(e))    


def notify_all(update, context):
    if str(update.effective_user.id) == MASTER_TELE_ID:
        new_feature_message = update.message.text.partition(" ")[2]
        if not new_feature_message:
            update.message.reply_text("Please provide a message to send.")
            return

        keyboard = [
            [
                InlineKeyboardButton("Confirm Send", callback_data="confirm_send"),
                InlineKeyboardButton("Cancel", callback_data="cancel_send"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            f"Preview:\n{new_feature_message}",
            reply_markup=reply_markup,
        )
    return CS.NOTIFICATION

def notify_preview(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=f"Sending message to all in progress...",
        reply_markup=InlineKeyboardMarkup([]),
    )
    try:
        if query.data == "confirm_send" and str(update.effective_user.id) == MASTER_TELE_ID:
            new_feature_message = query.message.text.partition("\n")[2]
            no_of_users, no_of_error_users, error_message = send_new_feature_message(
                context, new_feature_message
            )

            response = f"Message sent to {no_of_users} users.\n{no_of_error_users} users failed to receive the message."
            if error_message:
                response += f"\nErrors:\n{error_message}"
            query.edit_message_text(text=response)
        elif query.data == "cancel_send":
            query.edit_message_text(text="Message sending cancelled.")
    except Exception as e:
        query.edit_message_text(
            text=ERROR_TEXT + "\nError:\n" + utils.sanitize_error_message(str(e))
        )
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
        CS.ADD_BACKLOG_ENTRY: [
            MessageHandler(Filters.text & ~Filters.command, add_backlog_entry)
        ],
    }

    # Quick add-related states and handlers
    quick_add_states = {
        CS.QUICK_ADD: [MessageHandler(Filters.text & ~Filters.command, quick_add)],
        CS.QUICK_ADD_CATEGORY: [CallbackQueryHandler(quick_add_category)],
        CS.QUICK_ADD_TRANSPORT: [CallbackQueryHandler(quick_add_transport)],
    }

    # Notify all users (admin)
    notification_states = {
        CS.NOTIFICATION: [CallbackQueryHandler(notify_preview)],
    }

    # Retrieve transaction-related states and handlers
    get_transaction_states = {
        CS.HANDLE_GET_TRANSACTION: [
            MessageHandler(Filters.text & ~Filters.command, handle_get_transaction)
        ],
        CS.HANDLE_GET_OVERALL: [
            MessageHandler(Filters.text & ~Filters.command, handle_get_overall)
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
            CommandHandler("getdaytransaction", get_day_transaction),
            CommandHandler("getoverall", get_overall),
            CommandHandler("backlog", backlog),
            CommandHandler("notifyall", notify_all)
        ],
        states={
            CS.SET_UP: [MessageHandler(Filters.text & ~Filters.command, set_up)],
            CS.RESET_UP: [CallbackQueryHandler(reset_up)],
            **config_states,
            **entry_states,
            **quick_add_states,
            **get_transaction_states,
            **add_income_states,
            **notification_states,
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(conv_handler)

    help_handler = CommandHandler("help", help)
    dispatcher.add_handler(help_handler)