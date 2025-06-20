import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import socket
import os
import json
import threading
from config import *

class FileTransferGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("File Transfer Client")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.socket = None
        self.connected = False
        self.selected_file_path = None  # Initialize this attribute
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(conn_frame, text="Server:").grid(row=0, column=0, sticky=tk.W)
        self.server_entry = ttk.Entry(conn_frame, width=20)
        self.server_entry.insert(0, SERVER_HOST)
        self.server_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=tk.W)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, str(SERVER_PORT))
        self.port_entry.grid(row=0, column=3, padx=(5, 10))
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=(5, 0))
        
        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=5, padx=(10, 0))
        
        # File operations frame
        ops_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        ops_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ops_frame.columnconfigure(1, weight=1)
        
        # Upload section
        ttk.Label(ops_frame, text="Upload File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        upload_frame = ttk.Frame(ops_frame)
        upload_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        upload_frame.columnconfigure(0, weight=1)
        
        self.selected_file_var = tk.StringVar(value="No file selected")
        self.file_label = ttk.Label(upload_frame, textvariable=self.selected_file_var, 
                                   relief="sunken", padding="5")
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_btn = ttk.Button(upload_frame, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=0, column=1)
        
        self.upload_btn = ttk.Button(upload_frame, text="Upload", command=self.upload_file, state="disabled")
        self.upload_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(ops_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Download section
        ttk.Label(ops_frame, text="Download File:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        download_frame = ttk.Frame(ops_frame)
        download_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        download_frame.columnconfigure(0, weight=1)
        
        # Create entry without placeholder_text parameter
        self.download_entry = ttk.Entry(download_frame)
        self.download_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Add placeholder functionality manually
        self.setup_placeholder(self.download_entry, "Enter filename to download")
        
        self.download_btn = ttk.Button(download_frame, text="Download", command=self.download_file, state="disabled")
        self.download_btn.grid(row=0, column=1)
        
        # Action buttons frame
        action_frame = ttk.Frame(ops_frame)
        action_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        self.list_btn = ttk.Button(action_frame, text="List Files", command=self.list_files, state="disabled")
        self.list_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.info_btn = ttk.Button(action_frame, text="File Info", command=self.get_file_info, state="disabled")
        self.info_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.delete_btn = ttk.Button(action_frame, text="Delete File", command=self.delete_file, state="disabled")
        self.delete_btn.grid(row=0, column=2)
        
        # Output text area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear output button
        self.clear_btn = ttk.Button(output_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.grid(row=1, column=0, pady=(5, 0))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(2, weight=1)
    
    def setup_placeholder(self, entry_widget, placeholder_text):
        """Add placeholder functionality to an entry widget"""
        entry_widget.placeholder_text = placeholder_text
        entry_widget.placeholder_active = True
        
        # Insert placeholder text
        entry_widget.insert(0, placeholder_text)
        entry_widget.config(foreground='grey')
        
        def on_focus_in(event):
            if entry_widget.placeholder_active:
                entry_widget.delete(0, tk.END)
                entry_widget.config(foreground='black')
                entry_widget.placeholder_active = False
        
        def on_focus_out(event):
            if not entry_widget.get():
                entry_widget.insert(0, placeholder_text)
                entry_widget.config(foreground='grey')
                entry_widget.placeholder_active = True
        
        entry_widget.bind('<FocusIn>', on_focus_in)
        entry_widget.bind('<FocusOut>', on_focus_out)
    
    def get_entry_text(self, entry_widget):
        """Get text from entry widget, accounting for placeholder"""
        if hasattr(entry_widget, 'placeholder_active') and entry_widget.placeholder_active:
            return ""
        return entry_widget.get()
    
    def log_message(self, message):
        """Add message to output text area"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
    
    def toggle_connection(self):
        """Toggle connection to server"""
        if not self.connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
    
    def connect_to_server(self):
        """Connect to the file transfer server"""
        try:
            host = self.server_entry.get().strip()
            port = int(self.port_entry.get().strip())
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # Add timeout
            self.socket.connect((host, port))
            
            self.connected = True
            self.status_label.config(text="Connected", foreground="green")
            self.connect_btn.config(text="Disconnect")
            
            # Enable operation buttons
            self.update_button_states()
            
            self.log_message(f"Connected to server {host}:{port}")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {str(e)}")
            self.log_message(f"Connection failed: {str(e)}")
            self.connected = False
    
    def disconnect_from_server(self):
        """Disconnect from the server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.connected = False
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")
        
        # Disable operation buttons
        self.update_button_states()
        
        self.log_message("Disconnected from server")
    
    def update_button_states(self):
        """Update button states based on connection and file selection"""
        if self.connected:
            # Enable download and list buttons when connected
            self.download_btn.config(state="normal")
            self.list_btn.config(state="normal")
            self.info_btn.config(state="normal")
            self.delete_btn.config(state="normal")
            
            # Enable upload button only if file is selected and connected
            if self.selected_file_path and os.path.exists(self.selected_file_path):
                self.upload_btn.config(state="normal")
            else:
                self.upload_btn.config(state="disabled")
        else:
            # Disable all operation buttons when disconnected
            self.upload_btn.config(state="disabled")
            self.download_btn.config(state="disabled")
            self.list_btn.config(state="disabled")
            self.info_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
    
    def browse_file(self):
        """Open file dialog to select file for upload"""
        file_path = filedialog.askopenfilename(
            title="Select File to Upload",
            filetypes=[
                ("Text files", "*.txt"),
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Document files", "*.pdf *.doc *.docx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file_var.set(os.path.basename(file_path))
            self.selected_file_path = file_path
            self.log_message(f"Selected file: {file_path}")
            
            # Update button states after file selection
            self.update_button_states()
    
    def upload_file(self):
        """Upload selected file to server"""
        # Validate file selection
        if not self.selected_file_path or not os.path.exists(self.selected_file_path):
            messagebox.showwarning("No File Selected", "Please select a valid file to upload first.")
            return
        
        # Validate connection
        if not self.connected or not self.socket:
            messagebox.showerror("Not Connected", "Please connect to server first.")
            return
        
        # Disable upload button during upload
        self.upload_btn.config(state="disabled")
        
        def upload_thread():
            try:
                file_path = self.selected_file_path
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                self.log_message(f"Starting upload of {filename} ({file_size} bytes)")
                
                # Send upload command
                command = f"{COMMANDS['UPLOAD']}|{filename}|{file_size}"
                self.log_message(f"Sending command: {command}")
                self.socket.send(command.encode('utf-8'))
                
                # Wait for server acknowledgment
                response = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                self.log_message(f"Server response: {response}")
                
                if response != "READY":
                    self.log_message(f"Server not ready: {response}")
                    messagebox.showerror("Server Error", f"Server not ready: {response}")
                    return
                
                # Send file data with progress updates
                with open(file_path, 'rb') as f:
                    sent_size = 0
                    while sent_size < file_size:
                        data = f.read(BUFFER_SIZE)
                        if not data:
                            break
                        self.socket.send(data)
                        sent_size += len(data)
                        
                        # Update progress bar
                        progress = (sent_size / file_size) * 100
                        self.progress_var.set(progress)
                        self.root.update_idletasks()
                
                # Receive final response
                response = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                self.log_message(f"Upload result: {response}")
                
                if response.startswith("SUCCESS"):
                    messagebox.showinfo("Upload Complete", "File uploaded successfully!")
                    # Clear file selection after successful upload
                    self.selected_file_path = None
                    self.selected_file_var.set("No file selected")
                else:
                    messagebox.showerror("Upload Failed", response)
                
                # Reset progress bar
                self.progress_var.set(0)
                
            except Exception as e:
                self.log_message(f"Upload error: {str(e)}")
                messagebox.showerror("Upload Error", f"Upload failed: {str(e)}")
                self.progress_var.set(0)
                
                # Try to reconnect if connection was lost
                if "Connection" in str(e) or "Socket" in str(e):
                    self.disconnect_from_server()
            
            finally:
                # Re-enable upload button
                self.update_button_states()
        
        # Run upload in separate thread to prevent GUI freezing
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def download_file(self):
        """Download file from server"""
        filename = self.get_entry_text(self.download_entry).strip()
        if not filename:
            messagebox.showwarning("No Filename", "Please enter a filename to download.")
            return
        
        if not self.connected:
            messagebox.showerror("Not Connected", "Please connect to server first.")
            return
        
        # Ask where to save the file
        save_path = filedialog.asksaveasfilename(
            title="Save Downloaded File As",
            defaultextension=".*",
            initialvalue=filename
        )
        
        if not save_path:
            return
        
        def download_thread():
            try:
                self.log_message(f"Starting download of {filename}")
                
                # Send download command
                command = f"{COMMANDS['DOWNLOAD']}|{filename}"
                self.socket.send(command.encode('utf-8'))
                
                # Receive file info
                response = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                response_parts = response.split('|')
                
                if response_parts[0] == "ERROR":
                    self.log_message(f"Download error: {response_parts[1]}")
                    messagebox.showerror("Download Error", response_parts[1])
                    return
                
                original_filename = response_parts[1]
                file_size = int(response_parts[2])
                
                # Send ready acknowledgment
                self.socket.send("READY".encode('utf-8'))
                
                # Receive file data with progress updates
                received_size = 0
                with open(save_path, 'wb') as f:
                    while received_size < file_size:
                        data = self.socket.recv(min(BUFFER_SIZE, file_size - received_size))
                        if not data:
                            break
                        f.write(data)
                        received_size += len(data)
                        
                        # Update progress bar
                        progress = (received_size / file_size) * 100
                        self.progress_var.set(progress)
                        self.root.update_idletasks()
                
                self.log_message(f"Download complete: {save_path}")
                messagebox.showinfo("Download Complete", f"File downloaded successfully to:\n{save_path}")
                
                # Reset progress bar
                self.progress_var.set(0)
                
            except Exception as e:
                self.log_message(f"Download error: {str(e)}")
                messagebox.showerror("Download Error", f"Download failed: {str(e)}")
                self.progress_var.set(0)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def list_files(self):
        """List all files on server"""
        if not self.connected:
            messagebox.showerror("Not Connected", "Please connect to server first.")
            return
        
        try:
            command = COMMANDS['LIST']
            self.socket.send(command.encode('utf-8'))
            
            response = self.socket.recv(BUFFER_SIZE * 4).decode('utf-8')
            print(f"[CLIENT] Received response: {response}")  # Debug line
            response_parts = response.split('|', 1)  # Split only on first |
            
            if response_parts[0] == "ERROR":
                self.log_message(f"List error: {response_parts[1]}")
                return
            
            if len(response_parts) < 2 or response_parts[1] == "No files available":
                self.log_message("No files available on server")
                return
            
            self.log_message("\n" + "="*80)
            self.log_message("Files on server:")
            self.log_message("-"*80)
            self.log_message(f"{'Original Name':<25} {'Size (bytes)':<15} {'Upload Time':<20} {'Client IP':<15}")
            self.log_message("-"*80)
            
            # Parse the file list
            files_data = response_parts[1].split('||')
            print(f"[CLIENT] Files data: {files_data}")  # Debug line
            
            for file_data in files_data:
                if file_data.strip():  # Skip empty entries
                    file_parts = file_data.split('|')
                    print(f"[CLIENT] File parts: {file_parts}")  # Debug line
                    if len(file_parts) >= 4:
                        self.log_message(f"{file_parts[0]:<25} {file_parts[1]:<15} {file_parts[2]:<20} {file_parts[3]:<15}")
            
            self.log_message("="*80)
            
        except Exception as e:
            self.log_message(f"List error: {str(e)}")
            messagebox.showerror("List Error", f"Failed to list files: {str(e)}")
            print(f"[CLIENT ERROR] List error: {e}")  # Debug line
    
    def get_file_info(self):
        """Get detailed information about a file"""
        filename = self.get_entry_text(self.download_entry).strip()
        if not filename:
            messagebox.showwarning("No Filename", "Please enter a filename to get info.")
            return
        
        if not self.connected:
            messagebox.showerror("Not Connected", "Please connect to server first.")
            return
        
        try:
            command = f"{COMMANDS['INFO']}|{filename}"
            self.socket.send(command.encode('utf-8'))
            
            response = self.socket.recv(BUFFER_SIZE * 2).decode('utf-8')
            response_parts = response.split('|', 1)
            
            if response_parts[0] == "ERROR":
                self.log_message(f"Info error: {response_parts[1]}")
                messagebox.showerror("File Info Error", response_parts[1])
                return
            
            info = json.loads(response_parts[1])
            
            info_text = f"""
File Information for: {filename}
{'='*50}
Filename: {info['filename']}
Original Filename: {info['original_filename']}
File Size: {info['file_size']} bytes
SHA256 Hash: {info['file_hash']}
Upload Time: {info['upload_time']}
Uploaded by: {info['client_ip']}
{'='*50}
"""
            self.log_message(info_text)
            
        except Exception as e:
            self.log_message(f"Info error: {str(e)}")
            messagebox.showerror("Info Error", f"Failed to get file info: {str(e)}")
    
    def delete_file(self):
        """Delete a file from server"""
        filename = self.get_entry_text(self.download_entry).strip()
        if not filename:
            messagebox.showwarning("No Filename", "Please enter a filename to delete.")
            return
        
        if not self.connected:
            messagebox.showerror("Not Connected", "Please connect to server first.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{filename}'?"):
            return
        
        try:
            command = f"{COMMANDS['DELETE']}|{filename}"
            self.socket.send(command.encode('utf-8'))
            
            response = self.socket.recv(BUFFER_SIZE).decode('utf-8')
            self.log_message(f"Delete result: {response}")
            
            if response.startswith("SUCCESS"):
                messagebox.showinfo("Delete Complete", "File deleted successfully!")
            else:
                messagebox.showerror("Delete Failed", response)
            
        except Exception as e:
            self.log_message(f"Delete error: {str(e)}")
            messagebox.showerror("Delete Error", f"Delete failed: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()

if __name__ == "__main__":
    app = FileTransferGUI()
    app.run()
