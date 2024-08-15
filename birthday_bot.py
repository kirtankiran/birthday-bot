import time
from datetime import datetime, timedelta
import pywhatkit as kit
import schedule

def load_birthdays(filename):
    birthdays = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 3:
                        date_str, name, phone = parts
                        birthdays.append((datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S"), name, phone))
                    else:
                        print(f"Skipping malformed line: {line}")
    except FileNotFoundError:
        print(f"Birthday file '{filename}' not found. Starting with an empty list.")
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
    return birthdays

def save_birthday(filename, birthday, name, phone):
    try:
        with open(filename, 'a') as file:
            file.write(f"{birthday.strftime('%Y-%m-%d %H:%M:%S')},{name},{phone}\n")
    except Exception as e:
        print(f"Error saving birthday: {e}")

def overwrite_birthdays(filename, birthdays):
    try:
        with open(filename, 'w') as file:
            for birthday, name, phone in birthdays:
                file.write(f"{birthday.strftime('%Y-%m-%d %H:%M:%S')},{name},{phone}\n")
    except Exception as e:
        print(f"Error overwriting birthdays: {e}")

def clear_birthdays(filename):
    try:
        with open(filename, 'w') as file:
            pass  # This will clear the file by opening it in write mode and doing nothing
    except Exception as e:
        print(f"Error clearing birthdays: {e}")

def add_birthdays(filename):
    try:
        num_birthdays = int(input("How many birthdays would you like to add? "))
        for _ in range(num_birthdays):
            date_time_str = input("Enter the date and time in the format YYYY-MM-DD HH:MM:SS: ")
            name = input("Enter the name of the person: ")
            phone = input("Enter the phone number of the person (in the format +countrycodephonenumber): ")
            
            new_birthday = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
            save_birthday(filename, new_birthday, name, phone)
            print(f"Added birthday for {name} on {new_birthday}.")
    except Exception as e:
        print(f"Error adding birthdays: {e}")

def list_birthdays(birthdays):
    if not birthdays:
        print("No birthdays found.")
    for i, (birthday, name, phone) in enumerate(birthdays):
        print(f"{i+1}. {name}: {birthday}, {phone}")

def update_birthday(filename):
    try:
        birthdays = load_birthdays(filename)
        list_birthdays(birthdays)
        
        index = int(input("Enter the number of the birthday you want to update: ")) - 1
        if 0 <= index < len(birthdays):
            date_time_str = input("Enter the new date and time in the format YYYY-MM-DD HH:MM:SS: ")
            name = input("Enter the new name of the person: ")
            phone = input("Enter the new phone number of the person (in the format +countrycodephonenumber): ")
            
            new_birthday = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
            birthdays[index] = (new_birthday, name, phone)
            overwrite_birthdays(filename, birthdays)
            print(f"Updated birthday for {name} on {new_birthday}.")
        else:
            print("Invalid selection.")
    except Exception as e:
        print(f"Error updating birthday: {e}")

def schedule_birthday_messages(birthdays):
    for target_time, person, phone in birthdays:
        current_time = datetime.now()
        if target_time > current_time:
            delay = (target_time - current_time).total_seconds()
            if delay < 120:  # Ensure at least 2 minutes lead time
                target_time = current_time + timedelta(minutes=2)
                delay = 120
            schedule.every().day.at(target_time.strftime("%H:%M:%S")).do(send_birthday_message, person=person, phone=phone)
            print(f"Scheduled message for {person} at {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"The target time for {person} has already passed.")

def send_birthday_message(person, phone):
    future_time = datetime.now() + timedelta(minutes=2)
    kit.sendwhatmsg(phone, f"Happy Birthday, {person}!", future_time.hour, future_time.minute)
    print(f"Wished {person} a happy birthday at {datetime.now()}")

def main():
    filename = 'birthday.txt'
    
    while True:
        action = input("Enter 'add' to add new birthdays, 'schedule' to schedule birthday messages, 'update' to update past birthdays, 'clear' to clear all birthdays, or 'exit' to exit: ").strip().lower()
        
        if action == 'add':
            add_birthdays(filename)
        elif action == 'schedule':
            birthdays = load_birthdays(filename)
            schedule_birthday_messages(birthdays)
            while True:
                schedule.run_pending()
                time.sleep(1)
        elif action == 'update':
            update_birthday(filename)
        elif action == 'clear':
            clear_birthdays(filename)
            print("All birthdays have been cleared.")
        elif action == 'exit':
            print("Exiting the program.")
            break
        else:
            print("Invalid option. Please enter 'add', 'schedule', 'update', 'clear', or 'exit'.")

if __name__ == "__main__":
    main()
