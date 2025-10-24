Library Management System

1. Overview:
The Library Management System is a web-based application developed with Flask, SQLAlchemy, and LayUI.
It provides librarians with tools to manage books, students, and borrowing records through a clear and responsive interface.

2. Key Features:
	Admin login and authentication for secure access.
	Book registration and search by title, author, or ISBN.
	Inventory management for adding or deleting book copies.
	Student information management with card status tracking.
	Fuzzy search support for easier book lookup.
	Responsive UI built with LayUI components.

3. Database Design:
	Book – Stores general book information (ISBN, title, author, publisher, category).
	Student – Contains personal and card information.
	Admin – Records librarian login credentials and permissions.
	Inventory – Tracks physical book copies via barcode.
	ReadBook – Logs borrowing and returning activities.

4. Technology Stack:
	Backend (Flask, SQLAlchemy),
	Frontend (HTML, CSS, LayUI),
	Database (SQLite / MySQL),
	Authentication (Flask-Login)