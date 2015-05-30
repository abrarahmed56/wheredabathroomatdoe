import string
import re
#from jeopardy.final_jeopardy import music as the_bae
from validate_email import validate_email
from werkzeug.security import generate_password_hash, check_password_hash
from dbhelper import *

PASSWORD_VALID_CHARS = string.ascii_letters + string.digits + string.punctuation
# Source: http://www.diveintopython.net/regular_expressions/phone_numbers.html
PHONE_REGEX = re.compile(r'''
                # don't match beginning of string, number can start anywhere
    (\d{3})     # area code is 3 digits (e.g. '800')
    \D*         # optional separator is any number of non-digits
    (\d{3})     # trunk is 3 digits (e.g. '555')
    \D*         # optional separator
    (\d{4})     # rest of number is 4 digits (e.g. '1212')
    \D*         # optional separator
    (\d*)       # extension is optional and can be any number of digits
    $           # end of string
    ''', re.VERBOSE)

def is_valid_email(email, check_db=False):
    if check_db and emailExists(email):
        return (False, "A user with this email already exists")
    if validate_email(email):
        return (True, "Successful")
    else:
        return (False, "Invalid email")

def is_valid_password(password):
    global PASSWORD_VALID_CHARS
    for char in password:
        if char not in PASSWORD_VALID_CHARS:
            return (False, "Invalid characters in password.")
    if 8 <= len(password) <= 50:
        return (True, "Successful")
    else:
        return (False, "Invalid password length")
    
def is_valid_telephone(number):
    number = PHONE_REGEX.search(number)
    if number == None:
        return (False, "Invalid telephone number")
    else:
        number = number.groups()
        return (True, number[0] + number[1] + number[2])

def hash_password(s):
    return generate_password_hash(s)

def check_password(hashed_password, try_password):
    return check_password_hash(hashed_password, try_password)

