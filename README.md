# PyGuard: A Simple Python Honeypot

---

This project provides a versatile honeypot manager that allows you to run various honeypots (SSH, HTTP, SMTP) for security research and testing. The honeypots simulate vulnerable services to attract and log malicious activity.

### Features
- **SSH Honeypot**: Simulates an SSH server to catch brute-force login attempts.
- **HTTP Honeypot**: Simulates a WordPress login page to log unauthorized login attempts.
- **SMTP Honeypot**: Simulates an SMTP server to catch malicious email login attempts.

### Prerequisites
- Python 3.x
- The required dependencies, including `Flask`, `geoip2`, `Mailoney`, and others for each honeypot.

You can install the necessary dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### Running the Honeypot 

You can run any of the supported honeypots by specifying the relevant options:

#### SSH Honeypot
```bash
python honeypot.py -a <ADDRESS> -p <PORT> --ssh
```
This starts an SSH honeypot that listens for login attempts on the specified address and port.

#### HTTP WordPress Honeypot
```bash
python honeypot.py -a <ADDRESS> -p <PORT> --http
```
This starts a simulated WordPress login page that logs failed login attempts.

#### SMTP Honeypot
```bash
python honeypot.py -a <ADDRESS> -p <PORT> --smtp
```
This starts an SMTP honeypot that captures login attempts for malicious activity.

### Arguments

- `-a` or `--address`: The IP address to bind the honeypot.
- `-p` or `--port`: The port the honeypot will listen on.
- `-u` or `--username`: The username to use for login attempts (default is `admin`).
- `-pw` or `--password`: The password to use for login attempts (default is `password`).
- `--ssh`: Run an SSH honeypot.
- `--http`: Run a WordPress HTTP honeypot.
- `--smtp`: Run an SMTP honeypot.

### Example Commands

1. **SSH Honeypot on port 22**:
   ```bash
   python honeypot.py -a 0.0.0.0 -p 22 --ssh
   ```

2. **WordPress HTTP Honeypot on port 5000**:
   ```bash
   python honeypot.py -a 0.0.0.0 -p 5000 --http
   ```

3. **SMTP Honeypot on port 25**:
   ```bash
   python honeypot.py -a 0.0.0.0 -p 25 --smtp
   ```

### Logging
The honeypot logs all attempted logins (successful or unsuccessful) and the source IP addresses to a log file (`SMTP_audits.log` for SMTP, `http_audits.log` for HTTP, etc.). These logs can be used for analysis and further research.

