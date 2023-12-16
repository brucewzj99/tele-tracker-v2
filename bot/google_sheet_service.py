from google.oauth2 import service_account
from googleapiclient.discovery import build
from bot.common import EntryType
import os
import json

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


def get_main_dropdown_value(sheet_id, entry_type):
    range = []
    if entry_type == EntryType.TRANSPORT:
        range = transport_range
    elif entry_type == EntryType.OTHERS:
        range = others_main_range
    else:
        range = payment_main_range
    results = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range)
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


def get_sub_dropdown_value(sheet_id, main_value, entry_type):
    range = []
    if entry_type == EntryType.OTHERS:
        range = others_sub_range
    else:
        range = payment_sub_range
    results = (
        sheets_api.spreadsheets()
        .values()
        .batchGet(spreadsheetId=sheet_id, ranges=range)
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


def update_prev_day(sheet_id, month, first_row):
    last_row = get_new_row(sheet_id, month)
    # Write the message to the Google Sheet
    body = {"values": [[f"=SUM(C{first_row}:H{last_row})"]]}
    range_name = f"{month}!B{first_row}"
    sheets_api.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


def get_new_row(sheet_id, month):
    result = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"{month}!A:K")
        .execute()
    )
    values = result.get("values", [])
    return len(values)


def create_date(sheet_id, day, month, first_row):
    body = {"values": [[day]]}
    range_name = f"{month}!A{first_row}"
    sheets_api.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


def create_entry(sheet_id, month, row_tracker, row_data):
    entry_type = row_data[0]
    price = row_data[1].strip()
    remarks = row_data[2].strip()
    category = row_data[3].strip()
    payment = row_data[4].strip()

    data = [price, remarks, category, payment]
    sheet_column_start = "H"
    sheet_column_end = "K"
    if entry_type == EntryType.TRANSPORT:
        remarks_list = [remark.strip() for remark in remarks.split(",")]
        sheet_column_start = "C"
        sheet_column_end = "G"
        data = [price] + remarks_list + [category, payment]

    body = {"values": [data]}
    range_name = (
        f"{month}!{sheet_column_start}{row_tracker}:{sheet_column_end}{row_tracker}"
    )
    sheets_api.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


def get_trackers(sheet_id):
    result = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=tracker_range)
        .execute()
    )
    values = result.get("values", [])
    if values:
        return values[0]
    else:
        return


def update_rows(sheet_id, day, new_row, first_row):
    values = [[day] + [new_row] * 2 + [first_row]]
    range_name = tracker_range
    body = {"values": values}
    request = (
        sheets_api.spreadsheets()
        .values()
        .update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        )
    )
    request.execute()


def row_incremental(sheet_id, entry_type):
    range_name = tracker_range
    response = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range_name, majorDimension="ROWS")
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
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()


def get_quick_add_settings(sheet_id, entry_type):
    range_name = quick_add_range
    response = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range_name, majorDimension="ROWS")
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


def update_quick_add_settings(sheet_id, entry_type, payment, type):
    if entry_type == EntryType.TRANSPORT:
        range_1 = tracker_transport_1
        range_2 = tracker_transport_2
    else:
        range_1 = tracker_others_1
        range_2 = tracker_others_2

    last_row = (
        sheets_api.spreadsheets()
        .values()
        .get(
            spreadsheetId=sheet_id,
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
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


def get_quick_add_list(sheet_id, entry_type):
    if entry_type == EntryType.TRANSPORT:
        range_name = quick_transport_range
    else:
        range_name = quick_others_range
    response = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range_name)
        .execute()
    )

    values = response.get("values", [])
    settings_list = []
    for other in values:
        merged_str = ", ".join(other)
        settings_list.append(merged_str)
    return settings_list


def get_day_transaction(sheet_id, month, date):
    result = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"{month}!A:A")
        .execute()
    )
    values = result.get("values", [])
    flat_list = [item for sublist in values for item in sublist or [""]]

    first_row = flat_list.index(date)
    first_row += 1
    last_row = (
        flat_list.index(str(int(date) + 1))
        if str(int(date) + 1) in flat_list
        else first_row + 10
    )
    result = (
        sheets_api.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=sheet_id,
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


def get_work_place(sheet_id):
    result = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=income_range)
        .execute()
    )
    values = result.get("values", [])
    flattened_list = [item for sublist in values for item in sublist]

    return flattened_list


def update_income(sheet_id, month, row_data):
    data_mo = row_data[:3]
    data_r = [row_data[-1]]
    body_mo = {"values": [data_mo]}
    body_r = {"values": [data_r]}

    result = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"{month}!M5:M10")
        .execute()
    )
    values = result.get("values", [])
    last_row = len(values) + 5
    if last_row > 10:
        return False

    range_name_mo = f"{month}!M{last_row}:O{last_row}"
    range_name_r = f"{month}!R{last_row}:R{last_row}"
    sheets_api.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name_mo,
        valueInputOption="USER_ENTERED",
        body=body_mo,
    ).execute()

    body_r = {"values": [data_r]}
    sheets_api.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name_r,
        valueInputOption="USER_ENTERED",
        body=body_r,
    ).execute()
    return True


def get_overall(sheet_id, month):
    result = (
        sheets_api.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"{month}{overall_range}")
        .execute()
    )
    return result.get("values", [])
