# Configuration settings for the file transfer system
import os
import pathlib

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 8888
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 5

# Database configuration
DATABASE_NAME = 'file_transfer.db'

# File storage configuration
UPLOAD_DIRECTORY = 'uploads'
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Protocol constants
DELIMITER = b'=EOFX='
COMMANDS = {
    'UPLOAD': 'UPLOAD',
    'DOWNLOAD': 'DOWNLOAD',
    'LIST': 'LIST',
    'DELETE': 'DELETE',
    'INFO': 'INFO'
}

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'file_transfer.log'

# SSL/TLS configuration
SSL_ENABLED = True

_BASE_DIR = pathlib.Path(__file__).parent.parent  # project root (one level above src/)
SSL_CERT_FILE = str(_BASE_DIR / 'certs' / 'server.crt')
SSL_KEY_FILE  = str(_BASE_DIR / 'certs' / 'server.key')
