from google.oauth2 import service_account
from googleapiclient.discovery import build
from bot.common import EntryType
import os
import json
from bot.error_handler import GoogleSheetError

import datetime as dt
import pytz

timezone = pytz.timezone("Asia/Singapore")

GOOGLE_JSON = os.getenv("GOOGLE_JSON")
google_service = json.loads(GOOGLE_JSON)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_info(
    google_service, scopes=SCOPES
)
sheets_api = build("sheets", "v4", credentials=creds)

transport_range = "Dropdown!A3:A9"
others_sub_range = [f"Dropdown!{chr(i)}2:{chr(i)}9" for i in range(ord("B"), ord("K"))]
others_main_range = "Dropdown!B2:J2"
payment_sub_range = [
    f"Dropdown!{chr(i)}12:{chr(i)}19" for i in range(ord("A"), ord("K"))
]
payment_main_range = "Dropdown!A12:J12"
income_range = "Dropdown!L2:L9"
overall_range = "!M13:O25"

tracker_range = "Tracker!B3:E3"
tracker_transport_1 = "G"
tracker_transport_2 = "H"
tracker_others_1 = "I"
tracker_others_2 = "J"
quick_add_range = "Tracker!G3:J3"
quick_others_range = "Tracker!I3:J13"
quick_transport_range = "Tracker!G3:H13"

start_column_index = 0
end_column_index = 11


def get_main_dropdown_value(spreadsheet_id, entry_type):
    range = []
    if entry_type == EntryType.TRANSPORT:
        range = transport_range
    elif entry_type == EntryType.OTHERS:
        range = others_main_range
    else:
        range = payment_main_range

    try:
        results = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()
        )
        values = results.get("values", [])

        if entry_type == EntryType.TRANSPORT:
            results_list = []
            for sublist in values:
                for item in sublist:
                    results_list.append(item)
            return results_list

        return values[0]
    except Exception as e:
        raise GoogleSheetError(message=f"Error with retrieving values for main dropdown value for entrytype: {entry_type}", extra_info=str(e))



def get_sub_dropdown_value(spreadsheet_id, main_value, entry_type):
    range = []
    if entry_type == EntryType.OTHERS:
        range = others_sub_range
    else:
        range = payment_sub_range

    try:
        results = (
            sheets_api.spreadsheets()
            .values()
            .batchGet(spreadsheetId=spreadsheet_id, ranges=range)
            .execute()
        )

        value_ranges = results.get("valueRanges", [])

        dropdown = []
        for value in value_ranges:
            if value.get("values", []):
                if main_value == value.get("values", [])[0][0]:
                    dropdown.append(value.get("values", []))
                    pass

        flat_list = [item for sublist in dropdown[0] for item in sublist]
        return flat_list
    except Exception as e:
        raise GoogleSheetError(message=f"Error with retrieving values for sub dropdown value for entrytype: {entry_type}", extra_info=str(e))


def update_day_total_sum(spreadsheet_id, month, first_row, last_row=0):
    month = month.title()
    try:
        if last_row == 0:
            last_row = get_last_entered_row(spreadsheet_id, month)
        body = {"values": [[f"=SUM(C{first_row}:H{last_row})"]]}
        range_name = f"{month}!B{first_row}"
        sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise GoogleSheetError(message=f"Error with calculating sum for the previous day", extra_info=str(e))


def get_last_entered_row(spreadsheet_id, month):
    month = month.title()
    try:
        result = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"{month}!A:K")
            .execute()
        )
        values = result.get("values", [])
        return len(values)
    except Exception as e:
        raise GoogleSheetError(message=f"Error getting the last entered row for the month of {month}", extra_info=str(e))


def create_date(spreadsheet_id, day, month, first_row):
    month = month.title()

    body = {"values": [[day]]}
    range_name = f"{month}!A{first_row}"
    try:
        sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to create new day for {day} {month}", extra_info=str(e))


def create_entry(spreadsheet_id, month, row_tracker, row_data, backlog_day=None):
    entry_type, price, remarks, category, payment = (item.strip() if isinstance(item, str) else item for item in row_data)
    month = month.title()
    data = [price, remarks, category, payment]

    sheet_column_start = "A"
    sheet_column_end = "K"
    if entry_type == EntryType.TRANSPORT:
        remarks_list = [remark.strip() for remark in remarks.split(",")]
        data = [price] + remarks_list + [category, payment]
    else:
        data = [None] * 5 + data

    # prepend data
    if backlog_day:
        data = [backlog_day] + [None] + data
        body = {"values": [data]}
    else:
        data = [None] + [None] + data
        body = {"values": [data]}

    # creating the entry in google sheet
    try:
        range_name = (
            f"{month}!{sheet_column_start}{row_tracker}:{sheet_column_end}{row_tracker}"
        )
        sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to create new entry for {data}", extra_info=str(e))


def get_sheet_id_by_title(spreadsheet_id, title_to_find):
    try:
        sheet_metadata = (
            sheets_api.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        sheets = sheet_metadata.get("sheets", "")

        for sheet in sheets:
            title = sheet.get("properties", {}).get("title")
            if title == title_to_find:
                return sheet.get("properties", {}).get("sheetId")
        return None
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to retrieve sheet id by title: {title_to_find}", extra_info=str(e))

def move_row_down(spreadsheet_id, sheet_id, first_row_to_move, last_row_to_move):
    try:
        requests = [
            {
                "copyPaste": {
                    "source": {
                        "sheetId": sheet_id,
                        "startRowIndex": first_row_to_move - 1,
                        "endRowIndex": last_row_to_move,
                        "startColumnIndex": start_column_index,
                        "endColumnIndex": end_column_index,
                    },
                    "destination": {
                        "sheetId": sheet_id,
                        "startRowIndex": first_row_to_move,
                        "endRowIndex": last_row_to_move + 1,
                        "startColumnIndex": start_column_index,
                        "endColumnIndex": end_column_index,
                    },
                    "pasteType": "PASTE_NORMAL",
                    "pasteOrientation": "NORMAL",
                }
            }
        ]
        sheets_api.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        ).execute()
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to move existing entry down", extra_info=str(e))

def create_backlog_entry(spreadsheet_id, backlog_day, backlog_month, row_data):
    backlog_month = backlog_month.title()
    try:
        try:
            day_first_entry_index = get_day_first_entry_index(
                spreadsheet_id, backlog_month, backlog_day
            )
            first_row_to_move = int(get_first_row_to_move(spreadsheet_id, backlog_month, backlog_day))
            last_row_to_move = int(get_last_entered_row(spreadsheet_id, backlog_month))
            new_entry_row = first_row_to_move
            sheet_id = get_sheet_id_by_title(spreadsheet_id, backlog_month.title())

        if last_row_to_move >= first_row_to_move:
            move_row_down(spreadsheet_id, sheet_id, first_row_to_move, last_row_to_move)
            clear_range = f"{backlog_month}!A{new_entry_row}:K{new_entry_row}"
            sheets_api.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id, range=clear_range
            ).execute()

        # If there is no entry for the day, create a new date
        if day_first_entry_index is None:
            create_entry(spreadsheet_id, backlog_month, new_entry_row, row_data, backlog_day)
            day_first_entry_index = new_entry_row

        else:
            # Create the new entry in the new entry row and update day total
            create_entry(spreadsheet_id, backlog_month, new_entry_row, row_data)
        update_day_total_sum(spreadsheet_id, backlog_month, day_first_entry_index, new_entry_row)

        # datatime data
        current_datetime = dt.datetime.now(timezone)
        month = current_datetime.strftime("%b")

        # if backlog month is current month, need to update tracker to reflect backlog changes
        if backlog_month.title() == month:
            if last_row_to_move < first_row_to_move and day_first_entry_index == new_entry_row:
                update_tracker_values(spreadsheet_id, backlog_day, new_entry_row-1, new_entry_row)
            if last_row_to_move < first_row_to_move:
                row_incremental(spreadsheet_id, EntryType.OTHERS)
            else:
                row_incremental_all(spreadsheet_id)


    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to create backlog entry", extra_info=str(e))


def get_trackers(spreadsheet_id):
    try:
        result = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=tracker_range)
            .execute()
        )
        values = result.get("values", [])
        if values:
            return values[0]
        else:
            return
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to retrieve trackers", extra_info=str(e))


def update_tracker_values(spreadsheet_id, day, new_row, first_row):
    try:
        values = [[day] + [new_row] * 2 + [first_row]]
        range_name = tracker_range
        body = {"values": values}
        request = (
            sheets_api.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            )
        )
        request.execute()
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to update values for tracker", extra_info=str(e))


def row_incremental(spreadsheet_id, entry_type):
    range_name = tracker_range
    try:
        response = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name, majorDimension="ROWS")
            .execute()
        )

        values = response.get("values", [])
        if values:
            row_values = values[0]
            if entry_type == EntryType.OTHERS:
                row_values[1] = str(int(row_values[1]) + 1)  # Increment others count
            elif entry_type == EntryType.TRANSPORT:
                row_values[2] = str(int(row_values[2]) + 1)  # Increment transport count

            body = {"values": [row_values]}
            sheets_api.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute()
            
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to do tracker incremental update for {entry_type}", extra_info=str(e))


def row_incremental_all(spreadsheet_id):
    range_name = tracker_range
    try:
        response = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name, majorDimension="ROWS")
            .execute()
        )

        values = response.get("values", [])
        if values:
            row_values = values[0]
            row_values[1] = str(int(row_values[1]) + 1)  # Increment others count
            row_values[2] = str(int(row_values[2]) + 1)  # Increment transport count
            row_values[3] = str(int(row_values[3]) + 1)  # Increment first row count

            body = {"values": [row_values]}
            sheets_api.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute()
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to do tracker incremental update for all values", extra_info=str(e))

# This is used to retrieve the first quick add settings when there is only one
def get_quick_add_settings(spreadsheet_id, entry_type):
    range_name = quick_add_range
    try:
        response = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name, majorDimension="ROWS")
            .execute()
        )

        values = response.get("values", [])
        if values:
            if entry_type == EntryType.TRANSPORT:
                transport_payment = values[0][0] if len(values[0]) > 0 else None
                transport_type = values[0][1] if len(values[0]) > 1 else None
                return transport_payment, transport_type
            else:
                others_payment = values[0][2] if len(values[0]) > 2 else None
                others_type = values[0][3] if len(values[0]) > 3 else None
                return others_payment, others_type

        return None
            
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to do retrieve quick add settings for {entry_type}", extra_info=str(e))


def update_quick_add_settings(spreadsheet_id, entry_type, payment, type):
    if entry_type == EntryType.TRANSPORT:
        range_1 = tracker_transport_1
        range_2 = tracker_transport_2
    else:
        range_1 = tracker_others_1
        range_2 = tracker_others_2
    try:
        last_row = (
            sheets_api.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"Tracker!{range_1}:{range_2}",
            )
            .execute()
            .get("values", [])
        )
        last_row = len(last_row) + 1
        range_name = f"Tracker!{range_1}{last_row}:{range_2}{last_row}"
        new_row = [payment, type]
        body = {"values": [new_row]}
        sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to do update quick add settings for {entry_type}", extra_info=str(e))


def get_quick_add_list(spreadsheet_id, entry_type):
    if entry_type == EntryType.TRANSPORT:
        range_name = quick_transport_range
    else:
        range_name = quick_others_range
    try:
        response = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )

        values = response.get("values", [])
        settings_list = []
        for other in values:
            merged_str = ", ".join(other)
            settings_list.append(merged_str)
        return settings_list
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to do retrieve quick add settings list for {entry_type}", extra_info=str(e))


def get_day_transaction(spreadsheet_id, month, date):
    month = month.title()
    try:
        try:
            result = (
                sheets_api.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=f"{month}!A:A")
                .execute()
            )
            values = result.get("values", [])
            flat_list = [item for sublist in values for item in sublist or [""]]
            if (date) not in flat_list:
                return None, None, None
            first_row = flat_list.index(date)
            first_row += 1
            last_row = (
                flat_list.index(str(int(date) + 1))
                if str(int(date) + 1) in flat_list
                else first_row + 10
            )
        except Exception as e:
            raise GoogleSheetError(message=f"Fail to retrieve the starting and ending rows for {month}", extra_info=str(e))
        
        try:
            result = (
                sheets_api.spreadsheets()
                .values()
                .batchGet(
                    spreadsheetId=spreadsheet_id,
                    ranges=[
                        f"{month}!B{first_row}",
                        f"{month}!C{first_row}:G{last_row}",
                        f"{month}!H{first_row}:K{last_row}",
                    ],
                )
                .execute()
            )
            value_ranges = result.get("valueRanges", [])
            total_spend = value_ranges[0].get("values", []) if len(value_ranges) > 0 else []
            transport_values = (
                value_ranges[1].get("values", []) if len(value_ranges) > 0 else []
            )
            other_values = value_ranges[2].get("values", []) if len(value_ranges) > 1 else []

            return total_spend, transport_values, other_values
        except Exception as e:
            raise GoogleSheetError(message=f"Fail to retrieve the transaction for {date} {month}", extra_info=str(e))
    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to retrieve transaction for {date} {month}", extra_info=str(e))


def get_first_row_to_move(spreadsheet_id, month, date):
    month = month.title()
    try:
        result = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"{month}!A:A")
            .execute()
        )
        values = result.get("values", [])
        flat_list = [item for sublist in values for item in sublist or [""]]
        next_date = str(int(date) + 1)
        while next_date not in flat_list and int(next_date) < 32:
            next_date = str(int(next_date) + 1)

        try:
            last_row = flat_list.index(next_date)
        except ValueError:
            return get_last_entered_row(spreadsheet_id, month) + 1
        return last_row + 1
    except GoogleSheetError as e:
        raise e
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to find the first row to move", extra_info=str(e))


def get_day_first_entry_index(spreadsheet_id, month, date):
    month = month.title()
    try:
        result = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"{month}!A:A")
            .execute()
        )
        values = result.get("values", [])
        flat_list = [item for sublist in values for item in sublist or [""]]
        if (date) not in flat_list:
            return None
        first_row = flat_list.index(date)
        first_row += 1

        return first_row

    except Exception as e:
        raise GoogleSheetError(message=f"Fail to retrieve the index for first entry", extra_info=str(e))

def get_work_place(spreadsheet_id):
    try:
        result = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=income_range)
            .execute()
        )
        values = result.get("values", [])
        flattened_list = [item for sublist in values for item in sublist]

        return flattened_list
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to retrieve income sources", extra_info=str(e))


def update_income(spreadsheet_id, month, row_data):
    month = month.title()

    data_mo = row_data[:3]
    data_r = [row_data[-1]]
    body_mo = {"values": [data_mo]}
    body_r = {"values": [data_r]}
    try:
        result = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"{month}!M5:M10")
            .execute()
        )
        values = result.get("values", [])
        last_row = len(values) + 5
        if last_row > 10:
            return False

        range_name_mo = f"{month}!M{last_row}:O{last_row}"
        range_name_r = f"{month}!R{last_row}:R{last_row}"
        sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name_mo,
            valueInputOption="USER_ENTERED",
            body=body_mo,
        ).execute()

        body_r = {"values": [data_r]}
        sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name_r,
            valueInputOption="USER_ENTERED",
            body=body_r,
        ).execute()
        return True
    except Exception as e:
        raise GoogleSheetError(message=f"Fail to update income for {month}", extra_info=str(e))

def get_overall(spreadsheet_id, month):
    month = month.title()
    try:
        result = (
            sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"{month}{overall_range}")
            .execute()
        )
        return result.get("values", [])

    except Exception as e:
        raise GoogleSheetError(message=f"Fail to retrieve overall for {month}", extra_info=str(e))