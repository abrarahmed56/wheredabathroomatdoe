import string
import re
#from jeopardy.final_jeopardy import music as the_bae
from validate_email import validate_email
from werkzeug.security import generate_password_hash, check_password_hash

PASSWORD_VALID_CHARS = string.ascii_letters + string.digits + string.punctuation

def is_valid_email(email):
    # TODO verify that email is not already in the database
    return validate_email(email)

def is_valid_password(password):
    global PASSWORD_VALID_CHARS
    for char in password:
        if char not in PASSWORD_VALID_CHARS:
            return (False, "Invalid characters in password.")
    return 8 < len(password) < 50
    
def is_valid_telephone(number):
    filtered = re.findall(r'\D*([2-9]\d{2})(\D*)([2-9]\d{2})(\D*)(\d{4})\D*', number)
    if len(filtered) > 1:
        return (False, "Multiple phone numbers found.")
    filtered_string = ''.join(filtered[0])
    for char in filtered_string:
        if char not in string.digits:
            filtered_string = filtered_string.replace(char, '')
    return (True, filtered_string)

def hash_password(s):
    return generate_password_hash(s)

def check_password(hashed_password, try_password):
    return check_password_hash(hashed_password, try_password)

