import configparser
import logging

PROP_FILE = "config.properties"
config = configparser.RawConfigParser()
config.read(PROP_FILE)
ALIAS_SECTION = "alias"
# application's secrets
SECRETS = "secrets"
TOKEN = config.get(SECRETS, "telegram.token")
TELEGRAM_GROUP_ID = config.get(SECRETS, "telegram.group.id")
TELEGRAM_DEVELOPER_CHAT_ID = config.get(SECRETS, "telegram.developer.chat.id")
# application's settings
APPLICATION = "application"
SEND_START_AND_STOP_MESSAGE = config.get(APPLICATION, "send.start.and.stop.message")
HTTP_VERSION = config.get(APPLICATION, "http.version")
AIO_RATE_LIMITER_MAX_RETRIES = 10
case = config.get(APPLICATION, "log.level")
if case == "info":
	LOG_LEVEL = logging.INFO
elif case == "debug":
	LOG_LEVEL = logging.DEBUG
elif case == "error":
	LOG_LEVEL = logging.ERROR
else:
	LOG_LEVEL = logging.DEBUG
# messages
STARTUP_MESSAGE = "TGAliasBot started! "
STOP_MESSAGE = "TGAliasBot stopped!"
VERSION_MESSAGE = " - more info on https://github.com/simon387/TGAliasBot/blob/master/changelog.txt"
ERROR_NO_GRANT_SHUTDOWN = "You can't shutdown the bot!"
ALIAS_CREATED_OR_EDITED_MESSAGE = "Alias created or edited correctly!"
ERROR_ALIAS_CREATION = "Error on creating a new alias!"
ALIAS_DELETED_MESSAGE = "Alias deleted correctly"
ERROR_ALIAS_DELETION = "You need to specify the alias name!"
ERROR_ALIAS_NOT_FOUND = "Alias not found, delete aborted"
# urls

# var
SPACE = " "
EMPTY = ""
MP3 = "MP3"
MP4 = "MP4"
TRUE = "true"
W = 'w'
SLASH = '/'
