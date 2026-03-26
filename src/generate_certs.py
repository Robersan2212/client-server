"""
Generate a self-signed TLS certificate and private key for the file transfer server.
Run this script once before starting the server for the first time.

Usage:
    python src/generate_certs.py

Output:
    certs/server.crt  — public certificate (safe to commit, used by client for verification)
    certs/server.key  — private key (keep secret, listed in .gitignore)
"""

import subprocess
import os
import sys

CERTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'certs')
CERT_FILE = os.path.join(CERTS_DIR, 'server.crt')
KEY_FILE  = os.path.join(CERTS_DIR, 'server.key')


def generate():
    os.makedirs(CERTS_DIR, exist_ok=True)

    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print('[CERTS] Certificate and key already exist. Delete them to regenerate.')
        print(f'[CERTS] Certificate: {os.path.abspath(CERT_FILE)}')
        print(f'[CERTS] Private key:  {os.path.abspath(KEY_FILE)}')
        return

    print('[CERTS] Generating self-signed certificate (2048-bit RSA, valid 365 days)...')
    try:
        subprocess.run(
            [
                'openssl', 'req', '-x509',
                '-newkey', 'rsa:2048',
                '-keyout', KEY_FILE,
                '-out',    CERT_FILE,
                '-days',   '365',
                '-nodes',                  # no passphrase on the private key
                '-subj',   '/CN=localhost'  # Common Name must match the server hostname
            ],
            check=True,
            stderr=subprocess.DEVNULL  # suppress openssl progress output
        )
    except FileNotFoundError:
        print('[CERTS] ERROR: openssl not found. Install OpenSSL and ensure it is on your PATH.')
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f'[CERTS] ERROR: openssl command failed: {e}')
        sys.exit(1)

    print('[CERTS] Done.')
    print(f'[CERTS] Certificate: {os.path.abspath(CERT_FILE)}')
    print(f'[CERTS] Private key:  {os.path.abspath(KEY_FILE)}')
    print('[CERTS] Add certs/server.key to .gitignore — never commit the private key.')


if __name__ == '__main__':
    generate()
