import re
from collections import UserDict
from datetime import datetime, timedelta
import pickle



FRIDAY = 4
DATE_PATTERN = "%d.%m.%Y"
OPERATION_DAYS = range(0, 7)


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return e

    return inner



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
		pass


class Phone(Field):

    def __init__(self, value):
        if len(value) != 10:
            raise ValueError
        pattern = r'\d{10}'
        digits = re.findall(pattern, value)
        if not digits:
            raise ValueError("Invalid phone number")
        super().__init__(digits[0])


class Birthday(Field):
    
    def __init__(self, value: str):
        try:
            value = datetime.strptime(value, DATE_PATTERN)
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        item = Phone(phone)
        self.phones.append(item)

    def remove_phone(self, phone: str):
        phones_copy = self.phones.copy()
        for item in phones_copy:
            if item.value == phone:
                   self.phones.remove(item)
    
    def edit_phone(self, old_phone: str, new_phone: str):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)
           
    def find_phone(self, phone: str):
        res = ''
        for item in self.phones:
            if item.value == phone:
                   res = phone
        return res

    def add_birthday(self, birth_date: str):
         self.birthday = Birthday(birth_date)
            

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    
    def add_record(self, record: Record):
        self.data[record.name.value] = record
    
    def delete(self, name: str):
        self.data.pop(name)
    
    def find(self, name: str):
        return self.data.get(name)

    def get_upcoming_birthdays(self) -> list:
        result = []
        today = datetime.today().date()
        for name in self.data:
            record = self.find(name)
            birthday = record.birthday.value
            birthday_this_year = datetime(year=today.year, month=birthday.month, day=birthday.day)
            time_delta = birthday_this_year.date() - today
            if time_delta.days in OPERATION_DAYS:
                congratulation_offset = timedelta(7 - birthday_this_year.weekday()) if birthday_this_year.weekday() > FRIDAY else timedelta(days=0)
                congratulation_date = birthday_this_year + congratulation_offset
                result.append(dict(name=record.name.value, congratulation_date=congratulation_date.strftime(DATE_PATTERN)))
        return result



def parse_input(data: str):
    print(data)
    cmd, *args = data.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact already exists."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
        if phone:
            record.add_phone(phone)
    return message


@input_error
def edit_contact(args, book: AddressBook):
    print(args)
    name, old_phone, new_phone = args
    record = book.find(name)
    message = "Contact not exists."
    if record is not None:
        message = "Contact updated."
        record.edit_phone(old_phone, new_phone)
    return message


@input_error
def show_phone(args, book: AddressBook):
    record = book.find(args[0])
    if not record:        
        raise ValueError("Error: no such name.")
    return ' '.join(p.value for p in record.phones)


def show_all(book: AddressBook):
    res = ""
    for name in book.data:
        res += f"{name}: {show_phone([name], book)}\n"
    return res


@input_error
def add_birthday(args, book: AddressBook):
    name, birth_date = args
    record = book.find(name)
    if not record:
        raise ValueError("Error: no such name.")
    record.add_birthday(birth_date)
    return 'Birthday added'


@input_error
def show_birthday(args, book: AddressBook):
    record = book.find(args[0])
    if not record:        
        raise ValueError("Error: no such name.")
    return record.birthday.value.strftime(DATE_PATTERN)


def birthdays(args, book: AddressBook):
    data = book.get_upcoming_birthdays()
    res = ""
    for item in data:
            res += f"{item}\n"
    return res or "There are no upcoming birthdays"


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        output = ""

        if command in ("close", "exit"):
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            output = "How can I help you?"

        elif command == "add":
            output = add_contact(args, book)

        elif command == "change":
            output = edit_contact(args, book)

        elif command == "phone":
            output = show_phone(args, book)

        elif command == "all":
            output = show_all(book)

        elif command == "add-birthday":
            output = add_birthday(args, book)

        elif command == "show-birthday":
            output = show_birthday(args, book)

        elif command == "birthdays":
            output = birthdays(args, book)

        else:
            output = "Invalid command."

        print(output)

main()
