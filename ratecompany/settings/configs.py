import os


WEB_BASE_PATH = 'https://jobguy.work'
MEDIA_BASE_PATH = 'https://media.jobguy.work'
MEDIA_UPLOAD_PATH = 'https://upload.jobguy.work/company'

# cache
CACHE_FORGOT_PASSWORD_TOKEN = '_FORGOT_PASSWORD_TOKEN'
INTEGER_CONFIG_CACHE = 'INTEGER_CONFIG_CACHE_'
TIMEOUT_FORGOT_PASSWORD_TOKEN = 10 * 60
EMAIL_SEND_COUNT = 'EMAIL_SEND_COUNT_'
MAX_EMAIL_SEND_COUNT = 3
MAX_EMAIL_SEND_TIMEOUT = 60 * 60

COMPANY_LIST = 'COMPANY_LIST'
COMPANY_NAME_LIST = 'COMPANY_NAME_LIST'
CITY_CACHE_LIST = 'CITY_CACHE_LIST'

TOTAL = 'TOTAL'
LAST_INTERVIEWS = 'LAST_INTERVIEWS'
LAST_REVIEWS = 'LAST_REVIEWS'
DISCUSSED_COMPANY_LIST = 'DISCUSSED_COMPANY_LIST'
BEST_COMPANY_LIST = 'BEST_COMPANY_LIST'
INDUSTRY_LIST = 'INDUSTRY_LIST'
TOTAL_INTERVIEW = 'TOTAL_INTERVIEW'
TOTAL_REVIEW = 'TOTAL_REVIEW'
TOTAL_USER = 'TOTAL_USER'
TOTAL_COMPANY = 'TOTAL_COMPANY'

# types
MESSAGE_SHOW_TYPE = {'TOAST': 'TOAST', 'NONE': 'NONE'}
EMAIL_USERNAME = {'EMAIL': 'EMAIL', 'USERNAME': 'USERNAME'}
WORK_TIME_KIND = [('NORMAL', 'NORMAL'), ('OVERTIME', 'OVERTIME')]

KNOWN_EXTENSION = {'image/png': '.png', 'image/jpeg': '.jpeg', 'image/webp': '.webp'}

# model choices
VERY_SMALL = 'VS'
SMALL = 'S'
MEDIUM = 'M'
LARGE = 'L'
VERY_LARGE = 'VL'
ULTRA_LARGE = 'UL'
OFFICE_SIZE_CHOICES = (
    (VERY_SMALL, '1-10'),
    (SMALL, '11-50'),
    (MEDIUM, '51-200'),
    (LARGE, '201-500'),
    (VERY_LARGE, '501-1000'),
    (ULTRA_LARGE, 'More than 1000'),
)

STATE_CHOICES = (
    ('FULL', 'FULL TIME'),
    ('PART', 'PART TIME'),
    ('CONTRACT', 'CONTRACT'),
    ('INTERN', 'INTERN'),
    ('FREELANCE', 'FREELANCE'),
    ('REMOTE', 'REMOTE'),
)

INTERVIEW_STATUS = (
    ('WORKING', 'WORKING'),
    ('ACCEPT', 'ACCEPT'),
    ('REJECT', 'REJECT'),
    ('NORESPONSE', 'NORESPONSE'),
)

APPLY_METHOD = (
    ('CO_STAFF', 'CO_STAFF'),
    ('CO_SITE', 'CO_SITE'),
    ('JOB_SITE', 'JOB_SITE'),
    ('EMAIL', 'EMAIL'),
    ('FRIEND', 'FRIEND'),
    ('LINKEDIN', 'LINKEDIN'),
    ('FESTIVAL', 'FESTIVAL'),
    ('EVENT', 'EVENT'),
    ('OTHER', 'OTHER'),
)

RATE_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)

WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](
?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af
|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch
|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf
|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km
|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz
|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg
|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy
|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([
^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[
.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel
|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw
|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk
|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je
|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr
|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs
|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt
|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""


UPDATE_PERMISSION_DELTA = 30 * 24 * 60 * 60
UPDATE_LENGTH_PERCENT_PERMISSION = 95/100


IS_DELETED_TEXT ="شرکت %s درخواست رسمی خود را مبنی بر عدم به اشتراک گذاری این اطلاعات بر روی پلتفرم جابگای ابلاغ کرده " \
                 "و به این منظور جابگای مجبور به حذف این اطلاعات میباشد."

DONATE_LIST = 'DONATE_LIST'

GOOGLE_OAUTH_ID = os.environ.get('GOOGLE_OAUTH_ID', None)

if not GOOGLE_OAUTH_ID:
    raise Exception('Add GOOGLE_OAUTH_ID env variable, example: export GOOGLE_OAUTH_ID=123456')

BOT_APPROVE_KEY = os.environ.get('BOT_APPROVE_KEY', None)

if not BOT_APPROVE_KEY:
    raise Exception('Add BOT_APPROVE_KEY env variable, example: export BOT_APPROVE_KEY=123456')

MEDIA_UPLOAD_TOKEN = os.environ.get('MEDIA_UPLOAD_TOKEN', None)

if not MEDIA_UPLOAD_TOKEN:
    raise Exception('Add MEDIA_UPLOAD_TOKEN env variable, example: export MEDIA_UPLOAD_TOKEN=123456')

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', None)

if not TELEGRAM_BOT_TOKEN:
    raise Exception('Add TELEGRAM_BOT_TOKEN env variable, example: export TELEGRAM_BOT_TOKEN=123456')

