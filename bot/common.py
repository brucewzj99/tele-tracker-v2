from enum import Enum


class EntryType(Enum):
    TRANSPORT = "Transport"
    OTHERS = "Others"


class ConversationState(Enum):
    (
        SET_UP,
        RESET_UP,
        CONFIG_HANDLER,
        START_DESTINATION,
        ENTRY,
        PRICE,
        REMARKS,
        CATEGORY,
        SUBCATEGORY,
        PAYMENT,
        SUBPAYMENT,
        QUICK_ADD,
        QUICK_ADD_CATEGORY,
        QUICK_ADD_TRANSPORT,
        CONFIG_SETUP,
        CONFIG_CATEGORY,
        CONFIG_SUBCATEGORY,
        CONFIG_PAYMENT,
        CONFIG_SUBPAYMENT,
        HANDLE_GET_TRANSACTION,
        HANDLE_GET_OVERALL,
        INCOME,
        WORK_PLACE,
        CPF,
        BACKLOG,
        ADD_BACKLOG_ENTRY,
    ) = range(26)
