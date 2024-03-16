from googleapiclient.errors import HttpError
from functools import wraps

# Custom exception classes defined here


def google_sheets_exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            if e.resp.status == 401:
                raise AuthenticationError(
                    "Authentication failed: Check your credentials."
                )
            elif e.resp.status == 404:
                raise SpreadsheetNotFoundError(
                    "Spreadsheet not found: Check your spreadsheet ID."
                )
            else:
                raise APIRequestError(
                    f"API request failed with status {e.resp.status}: {e.error_details}"
                )
        except Exception as e:
            raise SheetsServiceError(f"An unexpected error occurred: {str(e)}")

    return wrapper


class SheetsServiceError(Exception):
    """Base class for exceptions in this module."""

    pass


class AuthenticationError(SheetsServiceError):
    """Raised when there's an issue with authentication or credentials."""

    pass


class SpreadsheetNotFoundError(SheetsServiceError):
    """Raised when a specified spreadsheet cannot be found."""

    pass


class APIRequestError(SheetsServiceError):
    """Raised for errors related to making API requests to Google Sheets."""

    pass


class InvalidEntryTypeError(SheetsServiceError):
    """Raised when an invalid entry type is specified."""

    pass
