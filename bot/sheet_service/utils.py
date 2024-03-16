"""
utils.py

This file contains utility functions for the Google Sheet Services.

"""


def create_range(sheet, start_col, start_row, end_col=None, end_row=None):
    """
    Create a standard range string.
    Sample output: "Dropdown!A2:A9"
    """
    end_part = f":{end_col}{end_row}" if end_col and end_row else ""
    return f"{sheet}!{start_col}{start_row}{end_part}"


def create_complex_range(sheet, start_col_ord, end_col_ord, row_start, row_end):
    """
    Create a range string for complex cases.
    Sample output: ["Dropdown!B2:B9", "Dropdown!C2:C9", ...]
    """
    return [
        f"{sheet}!{chr(i)}{row_start}:{chr(i)}{row_end}"
        for i in range(start_col_ord, end_col_ord + 1)
    ]
