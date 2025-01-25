import logging
from logging.handlers import RotatingFileHandler
import paramiko
import socket
import threading
from datetime import datetime

# Constant variables
SSH_BANNER = "SSH-2.0-ImprovedSSHServer_2.0"
HOST_KEY = paramiko.RSAKey(filename='server.key')

# Enhanced Logger Setup
def setup_logger(name, log_file, level=logging.INFO, max_bytes=5000, backup_count=5):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

funnel_logger = setup_logger('funnellogger', 'log files/audits.log')
creds_logger = setup_logger('credslogger', 'log files/command_audits.log')

# Server Interface
class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind: str, chanid: int) -> int:
        return paramiko.OPEN_SUCCEEDED if kind == 'session' else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        funnel_logger.info(f'{self.client_ip} tried username: {username}, password: {password}')
        if self.input_username and self.input_password:
            return paramiko.AUTH_SUCCESSFUL if username == self.input_username and password == self.input_password else paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        return True

# Emulated Shell
# Emulated Shell with Backspace Support
def emulate_shell(channel,client_ip):
    channel.send(b'root-kali2$ ')
    command = b""
    while True:
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()
        command +=char
        if char ==b'\r':
            if command.strip() == b'exit':
                response = b'\n Goodbye!\n'
                channel.close()
            elif command.strip() == b'pwd':
                response = b"\n" + b"\\usr\\local" + b"\r\n"
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'whoami':
                response = b"\n"+b'corpuser1'+ b"\r\n"
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'ls':
                response = b"\n"+b'kali_ssh.conf'+ b"\r\n"
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'cat kali_ssh.conf':
                response = b"\n"+b'Go to example.com'+ b"\r\n"
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            else:
                response=b"\n"+b"Unknown Command '"+bytes(command.strip())+b"'\r\n"
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            channel.send(response)
            channel.send(b'root-kali2$ ')
            command = b""


# Client Handler
def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"{client_ip} connected.")
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        transport.add_server_key(HOST_KEY)
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        transport.start_server(server=server)
        channel = transport.accept(20)
        if channel is None:
            print(f"Connection from {client_ip} did not open a channel.")
            return
        banner = "Welcome to Improved SSH Server!\n\n"
        channel.send(banner.encode())
        emulate_shell(channel, client_ip)
    except Exception as error:
        print(f"Error: {error}")
    finally:
        transport.close()
        client.close()

# SSH Honeypot
def honeypot(address, port, username, password):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))
    socks.listen(100)
    print(f"SSH honeypot running on {address}:{port}")

    while True:
        try:
            client, addr = socks.accept()
            threading.Thread(target=client_handle, args=(client, addr, username, password)).start()
        except Exception as error:
            print(f"Error accepting connection: {error}")

# Launch Honeypot
if __name__ == '__main__':
    honeypot('0.0.0.0', 2223, 'admin', 'admin123')
