DB_NAME = "users"
DB_USER = "softdev"

APP_PORT = 8000
WEBSITE_URL_BASE = "http://www.chesley.party:%d" % APP_PORT

ID_USER = 0
ID_PLACE = 1
ID_REVIEW = 2
ID_TEMPORARY_URL = 3
ID_REPORTS_USERS = 4
ID_REPORTS_PLACES = 5

AUTH_REGISTER = 0
AUTH_LOGIN = 1
AUTH_VERIFY = 2
AUTH_PASSRESET = 3

TEMP_URL_EMAIL_CONFIRM = 'email-confirm'
TEMP_URL_PHONE_CONFIRM = 'phone-confirm'
TEMP_URL_PASSWORD_RESET = 'reset-password'

TEMP_URL_EXPIRY_TIME = "1 day"
TEMP_URL_TIMEOUT_PENDING = "10 minutes"

UPLOAD_FOLDER = "static/uploads"

USER_REPORT_LIMIT = 10
PLACE_REPORT_LIMIT = 10

GEO_LOCAL_RADIUS = 0.14

ALLOWED_EXTENSIONS = set(["png", "bmp", "jpg"])
ALLOWED_TYPES = set(["bench", "fountain", "bathroom"])
def is_allowed_file_ext(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
