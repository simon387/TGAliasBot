import configparser
import html
import json
import logging as log
import os
import signal
import sys
import time as time_os
import traceback
from logging.handlers import RotatingFileHandler

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, ContextTypes, Application, AIORateLimiter, MessageHandler, \
	filters

import Constants
from BotApp import BotApp

log.basicConfig(
	handlers=[
		RotatingFileHandler(
			'_TGAliasBot.log',
			maxBytes=10240000,
			backupCount=5
		),
		log.StreamHandler()
	],
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=Constants.LOG_LEVEL
)


async def send_version(update: Update, context: CallbackContext):
	log_bot_event(update, 'send_version')
	await context.bot.send_message(chat_id=update.effective_chat.id, text=get_version() + Constants.VERSION_MESSAGE)


async def send_shutdown(update: Update, context: CallbackContext):
	log_bot_event(update, 'send_shutdown')
	if update.effective_user.id == int(Constants.TELEGRAM_DEVELOPER_CHAT_ID):
		if Constants.SEND_START_AND_STOP_MESSAGE == Constants.TRUE:
			await context.bot.send_message(chat_id=Constants.TELEGRAM_GROUP_ID, text=Constants.STOP_MESSAGE, parse_mode=ParseMode.HTML)
		os.kill(os.getpid(), signal.SIGINT)
	else:
		await context.bot.send_message(chat_id=update.effective_chat.id, text=Constants.ERROR_NO_GRANT_SHUTDOWN)


async def post_init(app: Application):
	version = get_version()
	log.info("Starting TGAliasBot, " + version)
	if Constants.SEND_START_AND_STOP_MESSAGE == 'true':
		# await app.bot.send_message(chat_id=c.TELEGRAM_GROUP_ID, text=c.STARTUP_MESSAGE + version, parse_mode=ParseMode.HTML)
		await app.bot.send_message(chat_id=Constants.TELEGRAM_DEVELOPER_CHAT_ID, text=Constants.STARTUP_MESSAGE + version, parse_mode=ParseMode.HTML)


async def post_shutdown(app: Application):
	log.info("Shutting down, bot id=" + str(app.bot.id))


def log_bot_event(update: Update, method_name: str):
	msg = update.message.text
	user = update.effective_user.first_name
	uid = update.effective_user.id
	log.info("[method=" + method_name + '] Got this message from ' + user + "[id=" + str(uid) + "]" + ": " + msg)


# Log the error and send a telegram message to notify the developer. Attemp to restart the bot too
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
	# Log the error before we do anything else, so we can see it even if something breaks.
	log.error(msg="Exception while handling an update:", exc_info=context.error)
	# traceback.format_exception returns the usual python message about an exception, but as a
	# list of strings rather than a single string, so we have to join them together.
	tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
	tb_string = "".join(tb_list)
	# Build the message with some markup and additional information about what happened.
	# You might need to add some logic to deal with messages longer than the 4096 character limit.
	update_str = update.to_dict() if isinstance(update, Update) else str(update)
	message = (
		f"An exception was raised while handling an update\n"
		f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
		"</pre>\n\n"
		f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
		f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
		f"<pre>{html.escape(tb_string)}</pre>"
	)
	message = message[:4300]  # truncate to prevent error
	if message.count('</pre>') % 2 != 0:
		message += '</pre>'
	# Finally, send the message
	await context.bot.send_message(chat_id=Constants.TELEGRAM_DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
	# Restart the bot
	time_os.sleep(5.0)
	os.execl(sys.executable, sys.executable, *sys.argv)


def get_version():
	with open("changelog.txt") as f:
		firstline = f.readline().rstrip()
	return firstline


async def chat_check(update: Update, context: CallbackContext):
	log_bot_event(update, 'chat_check')
	msg = update.message.text
	if msg.startswith(Constants.SLASH) and msg != "/alias":
		arr = msg.split()
		cmd = arr[0]
		config = configparser.RawConfigParser()
		config.read(Constants.PROP_FILE)
		try:
			val = config.get(Constants.ALIAS_SECTION, cmd)
			text = val + Constants.SPACE + Constants.SPACE.join(arr[1:])
			await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
		except configparser.NoOptionError as e:
			log.info("Alias command not found!")
			log.error(e)


async def alias(update: Update, context: CallbackContext):
	log_bot_event(update, 'alias')
	msg = Constants.SPACE.join(context.args).strip()
	arr = msg.split()
	config = configparser.RawConfigParser()
	config.read(Constants.PROP_FILE)
	if len(arr) >= 2:
		old_cmd = arr[0]
		if not old_cmd.startswith(Constants.SLASH):
			old_cmd = Constants.SLASH + old_cmd
		new_cmd = arr[1]
		if not new_cmd.startswith(Constants.SLASH):
			new_cmd = Constants.SLASH + new_cmd
		config.set(Constants.ALIAS_SECTION, new_cmd, old_cmd)
		with open(Constants.PROP_FILE, Constants.W) as configfile:
			config.write(configfile, space_around_delimiters=False)
			await context.bot.send_message(chat_id=update.effective_chat.id, text=Constants.ALIAS_CREATED_OR_EDITED_MESSAGE)
	else:
		if len(arr) == 0:
			text = Constants.EMPTY
			for (each_key, each_val) in config.items(Constants.ALIAS_SECTION):
				text += each_key + " - " + each_val + "\n"
			await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
		else:
			await context.bot.send_message(chat_id=update.effective_chat.id, text=Constants.ERROR_ALIAS_CREATION)


async def delete_alias(update: Update, context: CallbackContext):
	log_bot_event(update, 'delete_alias')
	msg = Constants.SPACE.join(context.args).strip()
	arr = msg.split()
	if len(arr) > 0:
		alias_name = arr[0]
		if not alias_name.startswith(Constants.SLASH):
			alias_name = Constants.SLASH + alias_name
		config = configparser.RawConfigParser()
		config.read(Constants.PROP_FILE)
		try:
			if config.remove_option(Constants.ALIAS_SECTION, alias_name):
				with open(Constants.PROP_FILE, Constants.W) as configfile:
					config.write(configfile, space_around_delimiters=False)
					await context.bot.send_message(chat_id=update.effective_chat.id, text=Constants.ALIAS_DELETED_MESSAGE)
			else:
				await context.bot.send_message(chat_id=update.effective_chat.id, text=Constants.ERROR_ALIAS_NOT_FOUND)
		except configparser.NoOptionError as e:
			log.info("Alias command not found!")
			log.error(e)
	else:
		await context.bot.send_message(chat_id=update.effective_chat.id, text=Constants.ERROR_ALIAS_DELETION)


if __name__ == '__main__':
	application = ApplicationBuilder() \
		.token(Constants.TOKEN) \
		.application_class(BotApp) \
		.post_init(post_init) \
		.post_shutdown(post_shutdown) \
		.rate_limiter(AIORateLimiter(max_retries=Constants.AIO_RATE_LIMITER_MAX_RETRIES)) \
		.http_version(Constants.HTTP_VERSION) \
		.get_updates_http_version(Constants.HTTP_VERSION) \
		.build()
	application.add_handler(CommandHandler('version', send_version))
	application.add_handler(CommandHandler('shutdown', send_shutdown))
	application.add_handler(CommandHandler('alias', alias))
	application.add_handler(CommandHandler('delete_alias', delete_alias))
	application.add_handler(MessageHandler(filters.TEXT, chat_check))
	application.add_error_handler(error_handler)
	application.run_polling(allowed_updates=Update.ALL_TYPES)
