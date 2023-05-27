import os

GOOGLE_API_EMAIL = os.getenv("GOOGLE_API_EMAIL")

SETUP_TEXT = (
    "Please set up your Google sheet by following the steps below.\n\n"
    + "1. Go over to https://docs.google.com/spreadsheets/d/1dJgJk7YUoR0nYjNa_lgrMxpz-MehOo4SyfRitlasQo8/edit#gid=861838157\n"
    + "2. Go to File > Make a copy\n"
    + "3. Go to File > Share > Share with others\n"
    + "4. Add "
    + str(GOOGLE_API_EMAIL)
    + " as an editor\n"
    + "5. Copy your Google Sheet URL and send it over\n"
    + "Example: https://docs.google.com/spreadsheets/d/abcd1234/edit\n"
    + "6. Edit the Dropdown sheet accordingly\n"
)
ERROR_TEXT = "There seems to be an error, please try again later."
SUCCESS_LINK_TEXT = "Google sheet successfully linked! Please proceed to configure your Dropdown sheet.\nOnce completed, type /addentry to add your first entry!"
GSHEET_ERROR_TEXT = (
    "There seems to be an error linking your google sheet, please try again later."
)
GSHEET_WRONG_TEXT = (
    "That doesn't seem like a Google sheet link, are you sure? Try sending again."
)
END_TEXT = "Goodbye!"

DEFAULT_TRANSPORT_TEXT = "What is your mode of transport?"
DEFAULT_PAYMENT_TEXT = "What is your mode of payment?"
DEFAULT_CATEGORY_TEXT = "What category is this?"
DEFAULT_SUBCATEGORY_TEXT = "What subcategory is this?"

PRICE_DEFAULT_TEXT = "How much is the price? e.g. 1.50"
PRICE_RETRY_TEXT = "Please enter a valid price. e.g. 1.50"
ENTRY_TYPE_TEXT = "What type of entry is this?"
TRANSPORT_DEFAULT_TEXT = (
    "Please enter the start and end destination seperated by comma.\ne.g. Home, School"
)
REMARKS_DEFAULT_TEXT = "Please enter the remarks.\ne.g. Bought a new shirt"

BACK_TEXT = "<< Back"

QUICK_SETUP_TRANSPORT = "You have not set up your quick add settings for transport yet, please do so by typing /config"
QUICK_SETUP_OTHER = "You have not set up your quick add settings for others yet, please do so by typing /config"

HELP_TEXT = (
    "To get started, please type /start\n"
    + "Remember to configure your Dropdown sheet to get started on this bot.\n\n"
    + "To configure, type /config\n"
    + "To add entry, type /addentry\n"
    + "To add transport quickly, type /addtransport\n"
    + "To add others quickly, type /addothers\n"
)

RETRIEVE_TRANSACTION_TEXT = "Please specify the date and month you wish to retrieve from in this format: DD MMM\ne.g 16 Mar\nor use /cancel to exit"

ADD_INCOME_TEXT = "Add income\nPlease state your income followed by any remarks (optional): [income],[remarks]\ne.g. 2000, Something"
ADD_INCOME_RETRY_TEXT = (
    "Please follow this format: [income],[remarks]\ne.g. 2000, Something"
)
CHOOSE_INCOME_SOURCE_TEXT = "Please choose your income source"
CPF_TEXT = "Is there CPF?"
INCOME_LIMIT_TEXT = "You have exceed the number of income allowed! (max 6)"
