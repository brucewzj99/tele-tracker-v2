"""
sheet_api.py


"""

# sheets_api.py
from googleapiclient.discovery import build
from bot.common import EntryType
from bot.sheet_service.auth import get_credentials
from bot.sheet_service.sheets_range import *


class GoogleSheetsClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            creds = get_credentials()
            cls._instance = build("sheets", "v4", credentials=creds)
        return cls._instance


class DropdownManager:
    """
    This class is responsible for managing the Dropdown sheet in the google sheet.
    """

    def __init__(self):
        self.sheets_api = GoogleSheetsClient.get_instance()

    # to be rename as get_header_values
    def get_main_dropdown_value(self, spreadsheet_id, entry_type) -> list[str]:
        """
        This method gets the header values for the CATEGORY/PAYMENT of the transaction.
        """
        range = []
        if entry_type == EntryType.TRANSPORT:
            # actually if entry_type is transport shouldnt be calling this
            # but instead call get_sub_dropdown_value instead
            # will do something to make this change after refactoring
            range = TRANSPORT_RANGE
        elif entry_type == EntryType.OTHERS:
            range = OTHERS_MAIN_RANGE
        else:
            range = PAYMENT_MAIN_RANGE

        results = (
            self.sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()
        )

        values_results = results.get("values", [])

        # to remove this and probably move it to get_sub_dropdown_value
        if entry_type == EntryType.TRANSPORT:
            results_list = []
            for sublist in values_results:
                for item in sublist:
                    results_list.append(item)
            return results_list

        return values_results[0]

    # to be rename as get_sub_values
    def get_sub_dropdown_value(
        self, spreadsheet_id, header_value, entry_type
    ) -> list[str]:
        """
        This method gets the sub values for the CATEGORY/PAYMENT of the transaction.
        """
        range = []
        # if entry_type is transport, should be calling this instead of get_main_dropdown_value
        if entry_type == EntryType.OTHERS:
            range = OTHERS_SUB_RANGE
        else:
            range = PAYMENT_SUB_RANGE
        results = (
            self.sheets_api.spreadsheets()
            .values()
            .batchGet(spreadsheetId=spreadsheet_id, ranges=range)
            .execute()
        )

        value_results = results.get("valueRanges", [])

        dropdown = []
        for value in value_results:
            if value.get("values", []):
                if header_value == value.get("values", [])[0][0]:
                    dropdown.append(value.get("values", []))
                    pass

        result_list = [item for sublist in dropdown[0] for item in sublist]
        return result_list


class TrackerManager:
    """
    This class is responsible for managing the Tracker sheet in the google sheet.
    """

    def __init__(self):
        self.sheets_api = GoogleSheetsClient.get_instance()


class EntryManager:
    """
    This class is responsible for logging of transactions in the google sheet.
    """

    def __init__(self):
        self.sheets_api = GoogleSheetsClient.get_instance()

    def create_entry(self, spreadsheet_id, month, row_tracker, row_data):
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
        self.sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()


class SheetManager:
    """
    This class is responsible  for retrieving/moving the google sheet.
    """

    def __init__(self):
        self.sheets_api = GoogleSheetsClient.get_instance()

    def get_last_entered_row(self, spreadsheet_id, month):
        """
        This method gets the last entered row for the month.
        """
        result = (
            self.sheets_api.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"{month}!A:K")
            .execute()
        )
        values = result.get("values", [])
        return len(values)

    def update_day_total_sum(self, spreadsheet_id, month, first_row, last_row=0):
        """
        This method update the total amount spend for the previous day
        """
        if last_row == 0:
            last_row = self.get_last_entered_row(spreadsheet_id, month)
        body = {"values": [[f"=SUM(C{first_row}:H{last_row})"]]}
        range_name = f"{month}!B{first_row}"
        self.sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def create_date(self, spreadsheet_id, day, month, first_row):
        """
        This method creates the date for the day.
        """
        body = {"values": [[day]]}
        range_name = f"{month}!A{first_row}"
        self.sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def get_sheet_id_by_title(self, spreadsheet_id, title_to_find):
        sheet_metadata = (
            self.sheets_api.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        sheets = sheet_metadata.get("sheets", "")

        for sheet in sheets:
            title = sheet.get("properties", {}).get("title")
            if title == title_to_find:
                return sheet.get("properties", {}).get("sheetId")

        return None
