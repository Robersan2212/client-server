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

# Path to the src/ directory where the server and client scripts live
SRC_DIR   = os.path.join(os.path.dirname(__file__), 'src')

# Paths to the TLS certificate (public) and private key
# server.crt is safe to commit; server.key must stay out of version control
CERT_FILE = os.path.join(os.path.dirname(__file__), 'certs', 'server.crt')
KEY_FILE  = os.path.join(os.path.dirname(__file__), 'certs', 'server.key')

# Must match SERVER_HOST and SERVER_PORT in config.py
HOST = 'localhost'
PORT = 8888


def generate_certs():
    """
    Ensure the TLS certificate and private key exist before starting the server.

    If both files are already present, generation is skipped — certs are reused
    across restarts so the client's pinned certificate stays valid.

    If either file is missing, runs generate_certs.py which calls OpenSSL to
    produce a self-signed certificate (server.crt) and a 2048-bit RSA private
    key (server.key) valid for 365 days.

    Returns True if certs are ready, False if generation failed.
    """
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
    """
    Launch the file transfer server as a background subprocess.

    Uses Popen (non-blocking) instead of run() so this script can continue
    to the next step while the server initialises in parallel. The returned
    process handle is used later to shut the server down cleanly.
    """
    print('[START] Starting server...')
    process = subprocess.Popen(
        [sys.executable, os.path.join(SRC_DIR, 'sever.py')],
        cwd=SRC_DIR
    )
    return process


def wait_for_server(timeout=10):
    """
    Poll the server until it accepts a TLS connection or the timeout expires.

    A plain TCP probe is not used here because the server is TLS-only — it
    would treat a raw connection as a broken handshake and log an SSL error.
    Instead, a real TLS handshake is performed using the pinned certificate,
    then the connection is immediately closed. A successful handshake confirms
    the server is fully initialised and ready for the client.

    Retries every 0.5 seconds and prints a dot for each attempt so progress
    is visible in the terminal.

    Returns True if the server became ready within the timeout, False otherwise.
    """
    print(f'[START] Waiting for server on {HOST}:{PORT}...', end='', flush=True)

    # Build an SSL context that trusts only the server's self-signed certificate
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=CERT_FILE)
    context.check_hostname = False  # cert has no SAN extension (CN-only)

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            # Open a raw TCP connection then upgrade it to TLS
            raw = socket.create_connection((HOST, PORT), timeout=1)
            with context.wrap_socket(raw, server_hostname=HOST):
                # Handshake succeeded — server is ready
                print(' ready.')
                return True
        except (ConnectionRefusedError, OSError, ssl.SSLError):
            # Server not up yet — wait and retry
            print('.', end='', flush=True)
            time.sleep(0.5)

    print()  # newline after the dots
    return False


def launch_client():
    """
    Open the GUI client and block until the user closes it.

    Uses subprocess.run() (blocking) so main() only continues — and the server
    only shuts down — after the client window has been closed.
    """
    print('[START] Launching client...')
    process = subprocess.run(
        [sys.executable, os.path.join(SRC_DIR, 'gui_client.py')],
        cwd=SRC_DIR
    )
    return process.returncode


def main():
    """
    Orchestrate the full startup and shutdown sequence:
      1. Certificates  — generate if missing
      2. Server        — start in background, wait until TLS-ready
      3. Client        — launch GUI and block until it closes
      4. Shutdown      — terminate the server process cleanly
    """
    if not generate_certs():
        sys.exit(1)

    server = start_server()

    if not wait_for_server():
        print('[START] ERROR: Server did not become ready in time.')
        server.terminate()
        sys.exit(1)

    print('[START] Server is ready. Opening client.')
    launch_client()

    # Client window was closed — shut the server down gracefully
    print('[START] Client closed. Shutting down server...')
    server.terminate()
    server.wait()  # wait for the process to fully exit before this script ends
    print('[START] Done.')


if __name__ == '__main__':
    main()
