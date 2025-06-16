import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pygsheets
from datetime import datetime

# Списки администраторов и сотрудников
ADMINS = []  # Add admin Telegram IDs here
EMPLOYEES = {}  # Add employee Telegram IDs here

user_data = {}
API_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

CREDENTIALS_FILE = 'path/to/your/credentials.json'
SPREADSHEET_ID = 'YOUR_SHEET_ID'

def init_sheets():
    global worksheet
    try:
        client = pygsheets.authorize(service_file=CREDENTIALS_FILE)
        sheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = sheet.sheet1
        return True
    except Exception as e:
        print(f"Error initializing sheets: {e}")
        return False
    except

def write_to_sheets(data):
    try:
        contract_number = data['contract_number']
        forwarder = data['forwarder']
        delivery_date = ""
        detail = data['detail']
        comment = data['comment']
        all_values = worksheet.get_all_values()
        next_row = len([row for row in all_values if any(row)]) + 1
        worksheet.update_values(crange=f'A{next_row}:E{next_row}', values=[[contract_number, forwarder, delivery_date, detail, comment]])
        return True
    except Exception as e:
        print(f"Error writing to sheet: {e}")
        return False
    except

def mark_delivery_completed(row_num):
    try:
        worksheet.refresh()
        all_values = worksheet.get_all_values()
        if row_num > len(all_values) or not all_values[row_num-1]:
            return False
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cell = pygsheets.Cell(f'C{row_num}', current_time)
        cell.color = (144/255, 238/255, 144/255, 1)
        worksheet.update_cells([cell])
        return True
    except Exception as e:
        print(f"Error marking delivery: {e}")
        return False
    except

def get_employee_history(employee_name):
    worksheet.refresh()
    all_values = worksheet.get_all_values()
    history = [(i + 1, row) for i, row in enumerate(all_values[1:], start=1) if row and len(row) >= 2 and row[1] == employee_name]
    return history if history else [("No history.", [])]

def get_main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    if chat_id in ADMINS:
        markup.add(InlineKeyboardButton("Admin Panel", callback_data="admin_panel"))
    else:
        markup.add(InlineKeyboardButton("Add Record", callback_data="add_record"))
        markup.add(InlineKeyboardButton("Personal Cabinet", callback_data="personal_cabinet"))
    return markup

def get_admin_panel():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Employee List", callback_data="list_employees"))
    markup.add(InlineKeyboardButton("All History", callback_data="all_history"))
    markup.add(InlineKeyboardButton("Filter by Employee", callback_data="filter_by_employee"))
    markup.add(InlineKeyboardButton("Back", callback_data="back_to_main"))
    return markup

def get_employee_filter_menu():
    markup = InlineKeyboardMarkup()
    for emp_id, emp_name in EMPLOYEES.items():
        markup.add(InlineKeyboardButton(emp_name, callback_data=f"filter_{emp_name}"))
    markup.add(InlineKeyboardButton("Back", callback_data="admin_panel"))
    return markup

def get_cancel_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Cancel", callback_data="cancel_input"))
    return markup

def get_delivery_buttons(chat_id, history):
    markup = InlineKeyboardMarkup()
    for row_num, row in history:
        if len(row) <= 2 or not row[2]:
            markup.add(InlineKeyboardButton(f"Delivery for record {row_num-1}", callback_data=f"deliver_{row_num}"))
    markup.add(InlineKeyboardButton("Back", callback_data="back_to_main"))
    return markup

def send_long_message(chat_id, text):
    max_length = 4096
    parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    for part in parts:
        bot.send_message(chat_id, part)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in ADMINS and chat_id not in EMPLOYEES:
        bot.send_message(chat_id, "You are not authorized.")
        return
    bot.send_message(chat_id, "Welcome!", reply_markup=get_main_menu(chat_id))

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    if chat_id not in ADMINS and chat_id not in EMPLOYEES:
        bot.send_message(chat_id, "Access denied.")
        return

    if call.data == "add_record" and chat_id not in ADMINS:
        user_data[chat_id] = {'step': 1, 'data': {'forwarder': EMPLOYEES[chat_id]}}
        bot.send_message(chat_id, "Enter contract number:", reply_markup=get_cancel_button())
    elif call.data == "personal_cabinet" and chat_id not in ADMINS:
        employee_name = EMPLOYEES.get(chat_id, "")
        history = get_employee_history(employee_name)
        response = "Your history:\n" + "\n".join([f"{i+1}. {row[0]} | {row[1]} | {row[2] if len(row) > 2 else ''} | {row[3] if len(row) > 3 else ''} | {row[4] if len(row) > 4 else ''}" for i, (_, row) in enumerate(history)])
        send_long_message(chat_id, response)
        if history and history != [("No history.", [])]:
            bot.send_message(chat_id, "Mark delivery:", reply_markup=get_delivery_buttons(chat_id, history))
    elif call.data.startswith("deliver_") and chat_id not in ADMINS:
        row_num = int(call.data.replace("deliver_", ""))
        if mark_delivery_completed(row_num):
            bot.send_message(chat_id, f"Delivery marked for record {row_num-1}.")
            employee_name = EMPLOYEES.get(chat_id, "")
            history = get_employee_history(employee_name)
            response = "Your history:\n" + "\n".join([f"{i+1}. {row[0]} | {row[1]} | {row[2] if len(row) > 2 else ''} | {row[3] if len(row) > 3 else ''} | {row[4] if len(row) > 4 else ''}" for i, (_, row) in enumerate(history)])
            send_long_message(chat_id, response)
            bot.send_message(chat_id, "Mark another delivery:", reply_markup=get_delivery_buttons(chat_id, history))
        else:
            bot.send_message(chat_id, "Error marking delivery.")
    elif call.data == "admin_panel" and chat_id in ADMINS:
        bot.send_message(chat_id, "Admin panel:", reply_markup=get_admin_panel())
    elif call.data == "list_employees" and chat_id in ADMINS:
        employees_list = "\n".join([f"{name} (ID: {eid})" for eid, name in EMPLOYEES.items()])
        bot.send_message(chat_id, f"Employee list:\n{employees_list}")
    elif call.data == "all_history" and chat_id in ADMINS:
        try:
            worksheet.refresh()
            all_values = worksheet.get_all_values()[1:]
            filled_rows = [row for row in all_values if row and len(row) >= 2 and any(cell.strip() for cell in row[:2])]
            if not filled_rows:
                bot.send_message(chat_id, "All history is empty.")
            else:
                history = "\n".join([f"{i+1}. {row[0]} | {row[1]} | {row[2] if len(row) > 2 else ''} | {row[3] if len(row) > 3 else ''} | {row[4] if len(row) > 4 else ''}" for i, row in enumerate(filled_rows)])
                send_long_message(chat_id, f"All history:\n{history}")
        except Exception as e:
            print(f"Error fetching history: {e}")
            bot.send_message(chat_id, "Error loading history.")
    elif call.data == "filter_by_employee" and chat_id in ADMINS:
        bot.send_message(chat_id, "Select employee to filter:", reply_markup=get_employee_filter_menu())
    elif call.data.startswith("filter_") and chat_id in ADMINS:
        employee_name = call.data.replace("filter_", "")
        if employee_name in EMPLOYEES.values():
            history = get_employee_history(employee_name)
            response = f"History for {employee_name}:\n" + "\n".join([f"{i+1}. {row[0]} | {row[1]} | {row[2] if len(row) > 2 else ''} | {row[3] if len(row) > 3 else ''} | {row[4] if len(row) > 4 else ''}" for i, (_, row) in enumerate(history)])
            send_long_message(chat_id, response)
        else:
            bot.send_message(chat_id, "Employee not found.")
    elif call.data == "back_to_main":
        bot.send_message(chat_id, "Back to main menu.", reply_markup=get_main_menu(chat_id))
    elif call.data == "cancel_input" and chat_id not in ADMINS:
        if chat_id in user_data:
            del user_data[chat_id]
        bot.send_message(chat_id, "Record addition canceled.", reply_markup=get_main_menu(chat_id))

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in ADMINS and chat_id not in EMPLOYEES:
        bot.send_message(chat_id, "You are not authorized.")
        return
    if chat_id not in user_data or 'step' not in user_data[chat_id]:
        bot.send_message(chat_id, "Use buttons to interact.", reply_markup=get_main_menu(chat_id))
        return

    step = user_data[chat_id]['step']
    if step == 1:
        if message.text.strip():
            user_data[chat_id]['data']['contract_number'] = message.text
            bot.send_message(chat_id, 'Enter position:', reply_markup=get_cancel_button())
            user_data[chat_id]['step'] = 2
        else:
            bot.send_message(chat_id, 'Contract number cannot be empty. Try again:', reply_markup=get_cancel_button())
    elif step == 2:
        if message.text.strip():
            user_data[chat_id]['data']['detail'] = message.text
            bot.send_message(chat_id, 'Enter comment (return reason):', reply_markup=get_cancel_button())
            user_data[chat_id]['step'] = 3
        else:
            bot.send_message(chat_id, 'Position cannot be empty. Try again:', reply_markup=get_cancel_button())
    elif step == 3:
        if message.text.strip():
            user_data[chat_id]['data']['comment'] = message.text
            if write_to_sheet(user_data[chat_id]['data']):
                bot.send_message(chat_id, 'Data saved successfully.', reply_markup=get_main_menu(chat_id))
            else:
                bot.send_message(chat_id, 'Error saving data. Restart bot with /start.')
            del user_data[chat_id]
        else:
            bot.send_message(chat_id, 'Comment cannot be empty. Try again:', reply_markup=get_cancel_button())

if __name__ == '__main__':
    init_sheets()
    bot.infinity_polling()