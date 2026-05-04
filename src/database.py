import sqlite3
import os
import hashlib
import secrets
from datetime import datetime
from config import DATABASE_NAME

class FileDatabase:
    def __init__(self):
        self.db_name = DATABASE_NAME
        print(f"[DATABASE] Initializing database: {os.path.abspath(self.db_name)}")
        self.init_database()
        self.test_database_connection()
    
    def test_database_connection(self):
        """Test database connection and show current contents"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"[DATABASE] Tables found: {tables}")
            
            # Count files
            cursor.execute("SELECT COUNT(*) FROM files")
            count = cursor.fetchone()[0]
            print(f"[DATABASE] Total files in database: {count}")
            
            # Show all files
            cursor.execute("SELECT * FROM files")
            all_files = cursor.fetchall()
            print(f"[DATABASE] All files: {all_files}")
            
            conn.close()
        except Exception as e:
            print(f"[DATABASE ERROR] Test connection failed: {e}")
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Create files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_hash TEXT NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    client_ip TEXT,
                    file_path TEXT NOT NULL
                )
            ''')
            
            # Create transfer_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transfer_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    operation TEXT NOT NULL,
                    client_ip TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    FOREIGN KEY (file_id) REFERENCES files (id)
                )
            ''')

            # Create users table — UNIQUE on username enforces deduplication at DB layer
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"[DATABASE] Database initialized successfully")
            
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to initialize database: {e}")
    
    def add_file(self, filename, original_filename, file_size, file_hash, client_ip, file_path):
        """Add a new file record to the database"""
        try:
            print(f"[DATABASE] Adding file: {original_filename} -> {filename}")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO files (filename, original_filename, file_size, file_hash, client_ip, file_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, original_filename, file_size, file_hash, client_ip, file_path))
            
            file_id = cursor.lastrowid
            conn.commit()
            
            # Verify the insert
            cursor.execute("SELECT COUNT(*) FROM files")
            count = cursor.fetchone()[0]
            print(f"[DATABASE] File added successfully. Total files now: {count}")
            
            conn.close()
            return file_id
            
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to add file: {e}")
            return None
    
    def get_file_info(self, filename):
        """Get file information by filename"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, filename, original_filename, file_size, file_hash, upload_time, client_ip, file_path
                FROM files WHERE filename = ? OR original_filename = ?
            ''', (filename, filename))
            
            result = cursor.fetchone()
            conn.close()
            print(f"[DATABASE] Get file info for '{filename}': {result}")
            return result
            
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to get file info: {e}")
            return None
    
    def list_files(self):
        """Get list of all files in the database"""
        try:
            print(f"[DATABASE] Listing files from database: {os.path.abspath(self.db_name)}")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # First, count total files
            cursor.execute("SELECT COUNT(*) FROM files")
            total_count = cursor.fetchone()[0]
            print(f"[DATABASE] Total files in database: {total_count}")
            
            # Get the file list
            cursor.execute('''
                SELECT original_filename, file_size, upload_time, client_ip, filename
                FROM files ORDER BY upload_time DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            print(f"[DATABASE] Query returned {len(results)} files")
            for i, result in enumerate(results):
                print(f"[DATABASE] File {i+1}: {result}")
            
            return results
            
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to list files: {e}")
            return []
    
    def delete_file(self, filename):
        """Delete file record from database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM files WHERE filename = ? OR original_filename = ?', (filename, filename))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            print(f"[DATABASE] Deleted {deleted_count} files matching '{filename}'")
            return deleted_count > 0
            
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to delete file: {e}")
            return False
    
    def log_transfer(self, file_id, operation, client_ip, status):
        """Log transfer operation"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transfer_logs (file_id, operation, client_ip, status)
                VALUES (?, ?, ?, ?)
            ''', (file_id, operation, client_ip, status))
            
            conn.commit()
            conn.close()
            print(f"[DATABASE] Logged transfer: {operation} for file_id {file_id}")
            
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to log transfer: {e}")

    def create_user(self, username, password):
        """
        Hash password with PBKDF2-SHA256 (310,000 iterations, OWASP 2023 recommendation)
        and insert a new user record. Returns True on success, False if username is taken.
        """
        try:
            # Generate a 256-bit random salt unique to this user
            salt = secrets.token_hex(32)
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                310_000
            ).hex()

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                (username, password_hash, salt)
            )
            conn.commit()
            conn.close()
            print(f"[DATABASE] User created: {username}")
            return True

        except sqlite3.IntegrityError:
            # UNIQUE constraint on username triggered — duplicate username
            print(f"[DATABASE] Username already exists: {username}")
            return False
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to create user: {e}")
            return False

    def verify_user(self, username, password):
        """
        Fetch stored hash and salt for the given username, recompute the hash
        from the supplied password, and compare using secrets.compare_digest
        (constant-time comparison to prevent timing attacks).
        Returns True if credentials are valid, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT password_hash, salt FROM users WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()
            conn.close()

            if row is None:
                return False  # username does not exist

            stored_hash, salt = row
            candidate_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                310_000
            ).hex()

            # Constant-time comparison prevents timing-based brute-force attacks
            return secrets.compare_digest(candidate_hash, stored_hash)

        except Exception as e:
            print(f"[DATABASE ERROR] Failed to verify user: {e}")
            return False

    def get_user(self, username):
        """Return (id, username) tuple for the given username, or None if not found."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            conn.close()
            return row
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to get user: {e}")
            return None


def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
