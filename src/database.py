import sqlite3
import os
import hashlib
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

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
