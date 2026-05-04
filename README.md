# Secure File Transfer System

A production-grade client-server file transfer application built in Python that demonstrates core competencies in network programming, applied cryptography, and secure software design.

## Overview

File transfer is a foundational network operation, yet most introductory implementations leave out the security layer entirely — transmitting data in plaintext with no concept of who is allowed to do what. This project addresses that gap by building a full-featured file transfer system where security is not an afterthought but a core design requirement.

The system allows authenticated users to upload, download, list, delete, and inspect files stored on a central server. Every connection is encrypted end-to-end with TLS, every user account is protected with industry-standard password hashing, and every file operation requires a valid JWT — making this a realistic model of how secure networked services are built in practice.

**Key security properties implemented:**

- **TLS/SSL transport encryption** — all data in transit is encrypted; plain TCP connections are rejected
- **JWT-based stateless authentication** — clients authenticate once and carry a signed, time-limited token for subsequent requests
- **PBKDF2-SHA256 password hashing** — passwords are stored as salted hashes using 310,000 iterations (OWASP 2023 recommendation), never in plaintext
- **Constant-time credential comparison** — login verification uses `secrets.compare_digest` to prevent timing-based brute-force attacks
- **SHA-256 file integrity verification** — every uploaded file is hashed server-side so corruption can be detected

This project demonstrates that security and usability can coexist: a Tkinter GUI client provides a clean graphical interface for all file operations, while the server handles multiple concurrent clients via threading.


# Network Communication

The project uses a Client-Server architecture. The server listens for incoming connections from multiple clients, processes their requests concurrently using threading, and manages file storage and database operations. The client connects to the server to send requests such as uploading, downloading, listing, deleting, and retrieving file information. This model centralizes control and data management on the server, while clients act as request initiators and receivers of responses.

Communication between the client and server is handled using TCP (Transmission Control Protocol), chosen for its reliable, connection-oriented data transfer—essential for maintaining file integrity during uploads and downloads. The server listens on port 8888 by default, and the client connects to this port on the specified server host (default is localhost).

# Development Environment

The software was developed using Python 3 as the primary programming language. Key libraries and modules include:

- **socket** — TCP network communication between client and server
- **ssl** — TLS/SSL wrapping for encrypted connections
- **threading** — concurrent client handling on the server side
- **sqlite3** — SQLite database for file metadata and transfer logs
- **hashlib** — SHA-256 file integrity hashing and PBKDF2 password hashing
- **secrets** — cryptographically secure salt generation and constant-time comparison
- **tkinter** — graphical user interface for the client, including file dialogs and progress bars
- **json** — structured data encoding for client-server messages
- **PyJWT** — JWT creation, signing, and validation


# Useful Websites

{Make a list of websites that you found helpful in this project}
* [NetworkAcademy.io](https://www.networkacademy.io/courses)
* [YouTube: Network Programming in Python (NEW!)](https://www.youtube.com/watch?v=6TzHMSk2Evc)
* [Socket Programming in Python (Guide) – Real Python](https://realpython.com/python-sockets/)
* [Socket Programming HOWTO – Python 3 Documentation](https://docs.python.org/3/howto/sockets.html)
* [User Datagram Client and Server – Python Module of the Week (PyMOTW)](https://pymotw.com/2/socket/udp.html)

# Future Work

* Add support for resuming interrupted uploads and downloads (chunked transfer with byte-range tracking)

* Implement per-user file ownership so users can only delete their own files

* Add a REST API layer as an alternative to the raw TCP protocol, enabling web and mobile clients

* Containerize the server with Docker and add a `docker-compose` configuration for one-command deployment

