import socket
import threading
import os
import json
from datetime import datetime
from config import *
from database import FileDatabase, calculate_file_hash

class FileTransferServer:
    def __init__(self):
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.db = FileDatabase()
        self.server_socket = None
        
    def start_server(self):
        """Start the file transfer server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CONNECTIONS)
            print(f"[SERVER] Listening on {self.host}:{self.port}")
            print(f"[SERVER] Upload directory: {UPLOAD_DIRECTORY}")
            print(f"[SERVER] Database: {DATABASE_NAME}")
            
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"[SERVER] Connection from {client_address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connections"""
        try:
            while True:
                # Receive command from client
                command_data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                if not command_data:
                    break
                
                print(f"[SERVER] Received command from {client_address}: {command_data}")
                
                # Parse command
                command_parts = command_data.split('|')
                command = command_parts[0]
                
                if command == COMMANDS['UPLOAD']:
                    self.handle_upload(client_socket, client_address, command_parts)
                elif command == COMMANDS['DOWNLOAD']:
                    self.handle_download(client_socket, command_parts)
                elif command == COMMANDS['LIST']:
                    self.handle_list(client_socket, client_address)
                elif command == COMMANDS['DELETE']:
                    self.handle_delete(client_socket, client_address, command_parts)
                elif command == COMMANDS['INFO']:
                    self.handle_info(client_socket, command_parts)
                else:
                    response = "ERROR|Unknown command"
                    client_socket.send(response.encode('utf-8'))
                
        except Exception as e:
            print(f"[SERVER ERROR] Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"[SERVER] Connection closed with {client_address}")
    
    def handle_upload(self, client_socket, client_address, command_parts):
        """Handle file upload from client"""
        try:
            filename = command_parts[1]
            file_size = int(command_parts[2])
            
            print(f"[SERVER] Starting upload: {filename} ({file_size} bytes)")
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
            
            print(f"[SERVER] Saving to: {file_path}")
            
            # Send acknowledgment
            client_socket.send("READY".encode('utf-8'))
            
            # Receive file data
            received_size = 0
            with open(file_path, 'wb') as f:
                while received_size < file_size:
                    data = client_socket.recv(min(BUFFER_SIZE, file_size - received_size))
                    if not data:
                        break
                    f.write(data)
                    received_size += len(data)
            
            print(f"[SERVER] Received {received_size}/{file_size} bytes")
            
            # Calculate file hash and add to database
            file_hash = calculate_file_hash(file_path)
            print(f"[SERVER] File hash: {file_hash}")
            
            file_id = self.db.add_file(
                unique_filename, filename, file_size, 
                file_hash, client_address[0], file_path
            )
            
            print(f"[SERVER] Added to database with ID: {file_id}")
            
            # Log the transfer
            self.db.log_transfer(file_id, 'UPLOAD', client_address[0], 'SUCCESS')
            
            response = f"SUCCESS|File uploaded successfully as {unique_filename}"
            client_socket.send(response.encode('utf-8'))
            print(f"[SERVER] Upload complete: {filename} -> {unique_filename}")
            
        except Exception as e:
            response = f"ERROR|Upload failed: {str(e)}"
            client_socket.send(response.encode('utf-8'))
            print(f"[SERVER ERROR] Upload failed: {e}")
    
    def handle_download(self, client_socket, command_parts):
        """Handle file download request"""
        try:
            filename = command_parts[1]
            file_info = self.db.get_file_info(filename)
            
            if not file_info:
                response = "ERROR|File not found"
                client_socket.send(response.encode('utf-8'))
                return
            
            file_path = file_info[7]  # file_path is at index 7
            file_size = file_info[3]  # file_size is at index 3
            
            if not os.path.exists(file_path):
                response = "ERROR|File not found on disk"
                client_socket.send(response.encode('utf-8'))
                return
            
            # Send file info
            response = f"DOWNLOAD|{file_info[2]}|{file_size}"  # original_filename, file_size
            client_socket.send(response.encode('utf-8'))
            
            # Wait for client acknowledgment
            ack = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            if ack != "READY":
                return
            
            # Send file data
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(BUFFER_SIZE)
                    if not data:
                        break
                    client_socket.send(data)
            
            # Log the transfer
            self.db.log_transfer(file_info[0], 'DOWNLOAD', client_socket.getpeername()[0], 'SUCCESS')
            print(f"[SERVER] File downloaded: {filename}")
            
        except Exception as e:
            response = f"ERROR|Download failed: {str(e)}"
            client_socket.send(response.encode('utf-8'))
            print(f"[SERVER ERROR] Download failed: {e}")
    
    def handle_list(self, client_socket, client_address):
        """Handle list files request"""
        try:
            print(f"[SERVER] Processing LIST request from {client_address}")
            
            # Get files from database
            files = self.db.list_files()
            print(f"[SERVER] Database returned {len(files)} files")
            
            if not files:
                response = "LIST|No files available"
                print(f"[SERVER] Sending: {response}")
            else:
                file_list = []
                for i, file_info in enumerate(files):
                    # file_info format: (original_filename, file_size, upload_time, client_ip, filename)
                    file_entry = f"{file_info[0]}|{file_info[1]}|{file_info[2]}|{file_info[3]}"
                    file_list.append(file_entry)
                    print(f"[SERVER] File {i+1}: {file_entry}")
                
                response = "LIST|" + "||".join(file_list)
                print(f"[SERVER] Final response length: {len(response)} characters")
                print(f"[SERVER] Sending response: {response[:200]}...")  # First 200 chars
            
            # Send response
            client_socket.send(response.encode('utf-8'))
            print(f"[SERVER] Response sent successfully")
            
            # Log the transfer
            self.db.log_transfer(None, 'LIST', client_address[0], 'SUCCESS')
            
        except Exception as e:
            response = f"ERROR|List failed: {str(e)}"
            client_socket.send(response.encode('utf-8'))
            print(f"[SERVER ERROR] List failed: {e}")
    
    def handle_delete(self, client_socket, client_address, command_parts):
        """Handle file deletion request"""
        try:
            filename = command_parts[1]
            file_info = self.db.get_file_info(filename)
            
            if not file_info:
                response = "ERROR|File not found"
                client_socket.send(response.encode('utf-8'))
                return
            
            # Delete from filesystem
            file_path = file_info[7]
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete from database
            success = self.db.delete_file(filename)
            
            if success:
                response = "SUCCESS|File deleted successfully"
                self.db.log_transfer(file_info[0], 'DELETE', client_address[0], 'SUCCESS')
            else:
                response = "ERROR|Failed to delete file from database"
            
            client_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            response = f"ERROR|Delete failed: {str(e)}"
            client_socket.send(response.encode('utf-8'))
    
    def handle_info(self, client_socket, command_parts):
        """Handle file info request"""
        try:
            filename = command_parts[1]
            file_info = self.db.get_file_info(filename)
            
            if not file_info:
                response = "ERROR|File not found"
            else:
                info = {
                    'filename': file_info[1],
                    'original_filename': file_info[2],
                    'file_size': file_info[3],
                    'file_hash': file_info[4],
                    'upload_time': file_info[5],
                    'client_ip': file_info[6]
                }
                response = f"INFO|{json.dumps(info)}"
            
            client_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            response = f"ERROR|Info failed: {str(e)}"
            client_socket.send(response.encode('utf-8'))

if __name__ == "__main__":
    server = FileTransferServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
