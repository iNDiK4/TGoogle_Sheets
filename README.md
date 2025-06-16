# Telegram Google Sheets Bot

A Telegram bot for managing delivery records in Google Sheets, with admin and employee interfaces.

## Features
- Employees: Add delivery records, view personal history, mark deliveries as completed
- Admins: View all employees, access full history, filter records by employee
- Records contract number, forwarder, delivery date, position, and comments
- Visual feedback with green highlight for completed deliveries
- Inline keyboard navigation
- Long message handling for large histories

## Prerequisites
- Python 3.8+
- `python-telegram-bot` and `pygsheets` libraries
- Google API credentials (JSON)
- Telegram Bot Token
- Google Sheets ID

## Installation
1. Clone the repository:
```bash
git clone https://github.com/iNDiK4/TGoogle_Sheets.git
```
2. Install dependencies:
```bash
pip install python-telegram-bot pygsheets
```
3. Set up Google API credentials:
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Download credentials JSON and update `CREDENTIALS_FILE` path in `telegram_sheets_bot.py`

## Usage
1. Configure the bot:
   - Set `API_TOKEN` in `bot.py`
   - Set `SPREADSHEET_ID` for your Google Sheet
   - Update `ADMINS` and `EMPLOYEES` with Telegram IDs
2. Run the bot:
```bash
python bot.py
```
3. Start the bot in Telegram with `/start`:
   - Employees: Add records or view history
   - Admins: Access admin panel for employee lists and history

## How It Works
- Employees add records (contract number, position, comment) to Google Sheets
- Employees mark deliveries as completed with timestamps
- Admins view all records or filter by employee
- Data is stored in a Google Sheet with columns: Contract Number, Forwarder, Delivery Date, Position, Comment
- Completed deliveries are highlighted in green

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
[MIT](LICENSE)
