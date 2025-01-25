import logging
from logging.handlers import RotatingFileHandler
from mailoney import Mailoney
import random

# Logging format
logging_format = logging.Formatter('%(asctime)s %(message)s')

# Set up HTTP logger to log malicious activity
funnel_logger = logging.getLogger('funnellogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('smtp_honeypot.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)


# Function to start the SMTP Honeypot using Mailoney
def start_smtp_honeypot(input_username='admin', input_password="password"):
    # Initialize the honeypot
    honeypot = Mailoney()

    # Set the SMTP server to listen on port 25 (default SMTP port)
    honeypot.listen(port=25, log_callback=log_activity, username=input_username, password=input_password)


# Callback to log all attempts
def log_activity(client_ip, username, password, is_valid):
    # Log each attempt
    location = "Unknown Location"

    # Log the activity
    funnel_logger.info(
        f"Client with IP {client_ip} attempted login with username: {username}, password: {password}. Valid: {is_valid}")

    # If the login was invalid, simulate random error messages
    if not is_valid:
        error_messages = [
            "Invalid username or password.",
            "User does not exist.",
            "Too many failed attempts. Please wait 15 minutes and try again."
        ]
        error_message = random.choice(error_messages)
        print(f"Invalid login attempt from {client_ip}: {username}/{password} - {error_message}")


# Run the SMTP honeypot
if __name__ == '__main__':
    print("Starting SMTP Honeypot on port 25...")
    start_smtp_honeypot(input_username='admin', input_password='password')
