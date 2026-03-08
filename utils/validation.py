import re


def validate_phone(phone):
    return bool(re.match(r"^\+63\d{10}$", phone))


def validate_email(email):
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))
