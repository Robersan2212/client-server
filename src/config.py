# Configuration settings for the file transfer system
import os

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
