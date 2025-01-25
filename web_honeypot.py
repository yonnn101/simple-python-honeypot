import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for
import geoip2.database
import random

# Load GeoLite2 database for geolocation
try:
    geo_reader = geoip2.database.Reader('GeoLite2-City.mmdb')  # Path to your GeoLite2 City database
except FileNotFoundError:
    print("GeoLite2 database file not found. Please make sure the file exists.")
    exit()

# logging format
logging_format = logging.Formatter('%(asctime)s %(message)s')

# http logger
funnel_logger = logging.getLogger('funnellogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('log files/http_audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# Web honeypot
def web_honeypot(input_username='admin', input_password="password"):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('wp-admin.html')  # Serve the login page template

    @app.route('/wp-admin-login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')

        # Geolocation lookup
        try:
            response = geo_reader.city(ip_address)
            location = f"{response.city.name}, {response.country.name}"
        except Exception as e:
            location = "Unknown Location"
            funnel_logger.error(f"GeoIP lookup failed for IP {ip_address}: {e}")

        # Log the login attempt with geolocation
        funnel_logger.info(f"IP Address: {ip_address} ({location}), User-Agent: {user_agent}, "
                           f"Attempted Username: {username}, Password: {password}")

        # Check if login is successful
        if username == input_username and password == input_password:
            return redirect(url_for('dashboard'))
        else:
            # Simulate a fake error message for invalid credentials
            error_messages = [
                "Invalid username or password.",
                "User does not exist.",
                "Too many failed attempts. Please wait 15 minutes and try again."
            ]
            return random.choice(error_messages)

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')  # Serve a fake dashboard page

    return app

def run_web_honeypot(port, input_username, input_password):
    run_web_honeypot_app = web_honeypot(input_username, input_password)
    run_web_honeypot_app.run(debug=True, port=port, host="0.0.0.0")

# Run the honeypot
if __name__ == '__main__':
    run_web_honeypot(port=5000, input_username='admin', input_password="password")
