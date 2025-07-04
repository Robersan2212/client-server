# Overview

As a software engineer focused on developing secure networking applications with Python, I designed and implemented a robust file transfer system to deepen my understanding of client-server architectures and real-world network communication. This project centers on building a reliable platform for transferring files between computers, emphasizing usability, extensibility, and data integrity.

[Software Demo Video](https://www.youtube.com/watch?v=jFMKMjRB1BI)

# Network Communication

The project uses a Client-Server architecture. The server listens for incoming connections from multiple clients, processes their requests concurrently using threading, and manages file storage and database operations. The client connects to the server to send requests such as uploading, downloading, listing, deleting, and retrieving file information. This model centralizes control and data management on the server, while clients act as request initiators and receivers of responses.

Communication between the client and server is handled using TCP (Transmission Control Protocol), chosen for its reliable, connection-oriented data transfer—essential for maintaining file integrity during uploads and downloads. The server listens on port 8888 by default, and the client connects to this port on the specified server host (default is localhost).

# Development Environment

The software was developed using Python 3 as the primary programming language, chosen for its simplicity, readability, and powerful standard libraries. Key libraries and modules include:

    socket: For TCP network communication between client and server

    threading: To handle multiple client connections concurrently on the server side

    sqlite3: To manage the SQLite database for storing file metadata and transfer logs

    hashlib: To compute SHA256 hashes for file integrity verification

    tkinter: To build the graphical user interface (GUI) for the client application, including file dialogs and progress bars

    json: For encoding and decoding structured data in communication messages


# Useful Websites

{Make a list of websites that you found helpful in this project}
* [NetworkAcademy.io](https://www.networkacademy.io/courses)
* [YouTube: Network Programming in Python (NEW!)](https://www.youtube.com/watch?v=6TzHMSk2Evc)
* [Socket Programming in Python (Guide) – Real Python](https://realpython.com/python-sockets/)
* [Socket Programming HOWTO – Python 3 Documentation](https://docs.python.org/3/howto/sockets.html)
* [User Datagram Client and Server – Python Module of the Week (PyMOTW)](https://pymotw.com/2/socket/udp.html)

# Future Work

* Add user authentication and access control for secure file operations

* Implement SSL/TLS encryption for all network communications

* Add support for resuming interrupted uploads and downloads

