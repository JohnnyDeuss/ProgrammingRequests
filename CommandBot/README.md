# CommandBot
A bot that performs commands messaged to it in the Facebook chat.

## Setup
Before starting, know that you'll need to be set up with an SSL certificate that is not self-signed.
Facebook is strict on security and only allows HTTPS connections and those connections have to be
secured with certificates from reputable certificate authorities.

1. [Install the Python requests module](https://requests.readthedocs.io/en/master/user/install/#install).
2. Install the WSGI module. Apache has mod_wsgi, nginx has uwsgi, though I've only tried this on Apache.
3. [Setup the app to use the Facebook API](https://developers.facebook.com/docs/messenger-platform/quickstart#steps).
	For the first snippet of JavaScript code, fill in the VERIFY_TOKEN variable.
	Once you have a page token, fill in the PAGE_ACCESS_TOKEN.
	
To test if the app is working, send a test command to the page that you've configured the bot to listen to in step 2.
Try sending "time" and seeing if you get a response, it may take a little while to respond (API's fault).
