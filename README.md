# Library Management System

## Overview
Library Management System is a web-based application built with Flask, SQLAlchemy, and LayUI. It helps librarians manage books, students, and circulation records through a clean, responsive interface, while allowing students to look up availability and view their own borrowing records.

## Key Features
Librarian (admin) features include secure login, new-book registration, inventory replenishment, circulation processing (borrowing and returns), student record lookup, and book deletion. Students can search books by multiple fields and view personal borrowing records with due dates, return status, and outstanding-fee status when applicable.

## Database Design
The schema models core entities and keeps data normalized to reduce duplication and improve consistency.

Book: stores book metadata (ISBN, title, author, publisher, category)  
Student: stores student profile and credentials  
Admin: stores librarian login credentials and permissions  
Inventory: tracks physical copies with barcode, location, and availability status  
ReadBook: logs borrow and return activities with dates and staff linkage

## Technology Stack
Backend: Flask, SQLAlchemy, Flask-Login  
Frontend: Jinja2 templates, LayUI, jQuery  
Database: SQLite (default)

## Installation
### 1) Clone the repo
```bash
git clone https://github.com/YiranZeng/404-NOT-FOUND.git
cd 404-NOT-FOUND
```
### 2) Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3) Install dependencies
```bash
pip install -r requirements.txt
```
### 4) Run the Application
```bash
python manage.py
```
Then open the browser and visit: http://127.0.0.1:5000/
