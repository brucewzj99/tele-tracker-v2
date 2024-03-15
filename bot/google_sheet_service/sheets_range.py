"""
sheets_range.py

This file contains the ranges for the Google Sheets Services for consistency.
The ranges are used to access specific cells in the Google Sheets.

"""

from bot.google_sheet_service.utils import create_range, create_complex_range

# Sheet names
DD_SHEET = "Dropdown"  # DD for Dropdown
TR_SHEET = "Tracker"  # TR for Tracker

# Tracker columns
TR_QUICKADD_TP_PAY = "G"  # Transport Payment Column
TR_QUICKADD_TP_TYPE = "H"  # Transport Type Column
TR_QUICKADD_OT_PAY = "I"  # Others Payment Column
TR_QUICKADD_OT_TYPE = "J"  # Others Type Column

TR_QUICKADD_ROW_START = 3  # Quick Add Row
TR_QUICKADD_ROW_END = 13  # Quick Add End Row

TR_START_COL = "B"  # Start Column
TR_END_COL = "E"  # End Column
TR_ROW = 3

# Dropdown rows
DD_MAIN_CAT_ROW = 2
DD_SUBCAT_START = 3
DD_SUBCAT_END = 9

DD_MAIN_PAY_ROW = 12
DD_SUBPAY_START = 13
DD_SUBPAY_END = 19

DD_TRANSPORT_COL = "A"
DD_OTHERS_COL_START = "B"
DD_OTHERS_COL_END = "J"

DD_INCOME_COL = "L"

DD_PAYMENT_COL_START = "A"
DD_PAYMENT_COL_END = "J"

# Column indexes
START_COL_IDX = 0
END_COL_IDX = 11

# Months
OVERALL_RANGE = "!M13:O25"

# Transport ranges
TRANSPORT_RANGE = create_range(
    DD_SHEET, DD_TRANSPORT_COL, DD_SUBCAT_START, DD_TRANSPORT_COL, DD_SUBCAT_END
)

# Others ranges
OTHERS_MAIN_RANGE = create_range(
    DD_SHEET, DD_OTHERS_COL_START, DD_MAIN_CAT_ROW, DD_OTHERS_COL_END, DD_MAIN_CAT_ROW
)

OTHERS_SUB_RANGE = create_complex_range(
    DD_SHEET,
    ord(DD_OTHERS_COL_START),
    ord(DD_OTHERS_COL_END),
    DD_MAIN_CAT_ROW,
    DD_SUBCAT_END,
)

# Payment ranges
PAYMENT_MAIN_RANGE = create_range(
    DD_SHEET, DD_PAYMENT_COL_START, DD_MAIN_PAY_ROW, DD_PAYMENT_COL_END, DD_MAIN_PAY_ROW
)

PAYMENT_SUB_RANGE = create_complex_range(
    DD_SHEET,
    ord(DD_PAYMENT_COL_START),
    ord(DD_PAYMENT_COL_END),
    DD_MAIN_PAY_ROW,
    DD_SUBPAY_END,
)

# Income range
INCOME_RANGE = create_range(
    DD_SHEET, DD_INCOME_COL, DD_MAIN_CAT_ROW, DD_INCOME_COL, DD_SUBCAT_END
)

# Tracker ranges
TRACKER_RANGE = create_range(TR_SHEET, TR_START_COL, TR_ROW, TR_END_COL, TR_ROW)

# Quick add ranges
QUICK_ADD_RANGE = create_range(
    TR_SHEET,
    TR_QUICKADD_TP_PAY,
    TR_QUICKADD_ROW_START,
    TR_QUICKADD_OT_TYPE,
    TR_QUICKADD_ROW_START,
)

QUICK_OTHERS_RANGE = create_range(
    TR_SHEET,
    TR_QUICKADD_OT_PAY,
    TR_QUICKADD_ROW_START,
    TR_QUICKADD_OT_TYPE,
    TR_QUICKADD_ROW_END,
)

QUICK_TRANSPORT_RANGE = create_range(
    TR_SHEET,
    TR_QUICKADD_TP_PAY,
    TR_QUICKADD_ROW_START,
    TR_QUICKADD_TP_TYPE,
    TR_QUICKADD_ROW_END,
)
