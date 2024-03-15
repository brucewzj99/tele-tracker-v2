"""
sheet_api.py


"""

# sheets_api.py
from googleapiclient.discovery import build
from bot.common import EntryType
from bot.google_sheet_service.auth import get_credentials
from bot.google_sheet_service.sheets_range import *


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


class SheetManager:
    """
    This class is responsible  for retrieving/moving the google sheet.
    """

    def __init__(self):
        self.sheets_api = GoogleSheetsClient.get_instance()
