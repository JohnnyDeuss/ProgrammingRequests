import json
import requests
import urllib
from datetime import datetime, timezone, timedelta

# I like defining dictionary keys as constants.
# All WSGI keys are upper case with underscores.
KEY_REQUEST_METHOD = "REQUEST_METHOD"
KEY_QUERY_STRING = "QUERY_STRING"
KEY_CONTENT_LENGTH = "CONTENT_LENGTH"
# Facebook API keys are always lowercase with underscores and periods.
# For verifying the script with Facebook.
KEY_MODE = "hub.mode"
KEY_VERIFY_TOKEN = "hub.verify_token"
KEY_CHALLENGE = "hub.challenge"
VERIFY_TOKEN = "<INSERT_VERIFY_TOKEN>"

KEY_OBJECT = "object"
KEY_ENTRY = "entry"
KEY_ID = "id"
KEY_MESSAGING = "messaging"
KEY_SENDER = "sender"
KEY_RECIPIENT = "recipient"
KEY_MESSAGE = "message"
KEY_TEXT = "text"

PAGE_ACCESS_TOKEN = "<INSERT_ACCESS_TOKEN>"
SEND_URL = "https://graph.facebook.com/v2.7/me/messages?access_token={}".format(PAGE_ACCESS_TOKEN)


def process_message(message, page_id):
	""" Process a single incoming message. """
	# Make sure it is a text message sent to the bot page.
	if message[KEY_RECIPIENT][KEY_ID] == page_id and KEY_MESSAGE in message and KEY_TEXT in message[KEY_MESSAGE]:
		# Perform the command if it exists.
		words = message[KEY_MESSAGE][KEY_TEXT].split()
		cmd = words[0]
		cmd_lower = cmd.lower()
		args = words[1:]
		user = message[KEY_SENDER][KEY_ID]
		try:
			if cmd_lower in COMMAND_HANDLERS:
				reply_text = COMMAND_HANDLERS[cmd_lower](args, message)
			else:
				reply_text = COMMAND_HANDLERS["help"](args, message)
		except Exception as e:
			reply_text = "You broke me with :(\n\nCommand: {}\nException {}\n{}".format(
					cmd, e.__class__.__name__, e.args)
		send_message(user, reply_text)


def handle_callback(post, start_response):
	""" Handle callbacks for incoming messages. """
	# Make sure the callback is from a page subscription.
	if KEY_OBJECT not in post or post[KEY_OBJECT] != "page":
		raise Exception

	for entry in post[KEY_ENTRY]:
		for message in entry[KEY_MESSAGING]:
			process_message(message, entry[KEY_ID])

	response_headers = [
		("Content-Type", "text/html"),
		("Content-Length", "0")
	]
	start_response("200 OK", response_headers)
	return [b""]


def verify_request(get, start_response):
	""" Respond to Facebook's verification when registering the app. """
	# Is subscribe event, has correct verification token and has a challenge.
	if (KEY_MODE in get and get[KEY_MODE][0] == "subscribe" and
				KEY_VERIFY_TOKEN in get and get[KEY_VERIFY_TOKEN][0] == VERIFY_TOKEN and
				KEY_CHALLENGE in get):
		response_body = get[KEY_CHALLENGE][0].encode("utf-8")
		response_headers = [
			("Content-Type", "text/html"),
			("Content-Length", str(len(response_body)))
		]
		start_response("200 OK", response_headers)
		return [response_body]
	else:
		start_response("400 Bad Request", [])
		return [b""]


def parse_post(env):
	""" Parses a POST request. """
	if KEY_CONTENT_LENGTH in env:
		length = int(env[KEY_CONTENT_LENGTH])
		return json.loads(env["wsgi.input"].read(length).decode())
	else:
		return {}


def parse_get(env):
	""" Parses a GET request. """
	return urllib.parse.parse_qs(env[KEY_QUERY_STRING])


def send_message(recipient, message):
	""" Send a Facebook message. """
	data = {"recipient": {"id": recipient}, "message": {"text": message}}
	r = requests.post(SEND_URL, json=data)


def application(env, start_response):
	"""
		Program entry point, respond to incoming Facebook messages.
		Incoming messages are parsed and any valid commands are executed.
	"""
	# GET requests are used by Facebook that the app is actually the app we say it is when registering.
	if env[KEY_REQUEST_METHOD] == "GET":
		get = parse_get(env)
		return verify_request(get, start_response)
	elif env[KEY_REQUEST_METHOD] == "POST":
		post = parse_post(env)
		return handle_callback(post, start_response)
		

#
# Command handlers:
# Every command handler gets passed an args list, which are the words that come after the command.
# The second parameter is the message object sent by Facebook, which includes more information about
# the message sent and the users involved.
#
def help(args, message):
	""" The default command handler, if no valid command is given. """
	return "Supported commands:\n"+"\n".join("- "+command for command in sorted(COMMAND_HANDLERS.keys()))


def get_ip_addr(args, message):
	""" Get this server's default IP address. """
	if not args:
		req = requests.get("https://icanhazip.com")
	elif args[0] == "4":
		req = requests.get("https://ipv4.icanhazip.com")
	elif args[0] == "6":
		req = requests.get("https://ipv6.icanhazip.com")
	else:
		return "Usage: ip [version].\nDescription: Get the IP address of the server.\nParameters:\nversion: <omitted>, 4 or 6.\nOmitted returns the default IP address used."
	return req.text.rstrip()


def get_local_time(args, message):
	""" Get the local server time. """
	d = datetime.now(timezone(timedelta(hours=2)))
	if not args:
		return d.strftime("%c")
	if args[0].lower() == "iso":
		return d.isoformat()
	else:
		return "Usage: time [format].\nDescription: Get the local time of the server.\nParameters:\nformat: <omitted>, human.\nOmitted returns a human-friendly format, iso returns the ISO format"

		
def get_user_id(args, message):
	""" Get the sending user's Facebook ID. """
	if not args:
		return message[KEY_SENDER][KEY_ID]
	else:
		return "Usage: user_id\nReturn your user ID, used by Facebook to identify you."

		
def get_bot_id(args, message):
	""" Get this bot's Facebook ID. """
	if not args:
		return message[KEY_RECIPIENT][KEY_ID]
	else:
		return "Usage: bot_id\nReturn this bot's ID, used by Facebook to identify you."


# Define which function should be called for which command.
COMMAND_HANDLERS = {
	"help": help,
	"ip": get_ip_addr,
	"time": get_local_time,
	"user_id": get_user_id,
	"bot_id": get_bot_id
}
