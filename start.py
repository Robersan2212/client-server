"""
Startup script for the file transfer application.

Steps:
  1. Generate TLS certificate and key if they don't exist
  2. Start the server in a background process
  3. Wait for the server to be ready
  4. Launch the GUI client
  5. When the client exits, shut down the server
"""

import subprocess
import sys
import os
import socket
import ssl
import time

SRC_DIR   = os.path.join(os.path.dirname(__file__), 'src')
CERT_FILE = os.path.join(os.path.dirname(__file__), 'certs', 'server.crt')
KEY_FILE  = os.path.join(os.path.dirname(__file__), 'certs', 'server.key')
HOST      = 'localhost'
PORT      = 8888


def generate_certs():
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print('[START] Certificates already exist — skipping generation.')
        return True

    print('[START] Generating TLS certificate...')
    result = subprocess.run(
        [sys.executable, os.path.join(SRC_DIR, 'generate_certs.py')],
        cwd=SRC_DIR
    )
    if result.returncode != 0:
        print('[START] ERROR: Certificate generation failed. Cannot continue.')
        return False

    print('[START] Certificate generated successfully.')
    return True


def start_server():
    print('[START] Starting server...')
    process = subprocess.Popen(
        [sys.executable, os.path.join(SRC_DIR, 'sever.py')],
        cwd=SRC_DIR
    )
    return process


def wait_for_server(timeout=10):
    print(f'[START] Waiting for server on {HOST}:{PORT}...', end='', flush=True)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=CERT_FILE)
    context.check_hostname = False

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            raw = socket.create_connection((HOST, PORT), timeout=1)
            with context.wrap_socket(raw, server_hostname=HOST):
                print(' ready.')
                return True
        except (ConnectionRefusedError, OSError, ssl.SSLError):
            print('.', end='', flush=True)
            time.sleep(0.5)
    print()
    return False


def launch_client():
    print('[START] Launching client...')
    process = subprocess.run(
        [sys.executable, os.path.join(SRC_DIR, 'gui_client.py')],
        cwd=SRC_DIR
    )
    return process.returncode


def main():
    if not generate_certs():
        sys.exit(1)

    server = start_server()

    if not wait_for_server():
        print('[START] ERROR: Server did not become ready in time.')
        server.terminate()
        sys.exit(1)

    print('[START] Server is ready. Opening client.')
    launch_client()

    print('[START] Client closed. Shutting down server...')
    server.terminate()
    server.wait()
    print('[START] Done.')


if __name__ == '__main__':
    main()
