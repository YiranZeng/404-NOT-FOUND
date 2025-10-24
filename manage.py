import os
from app import create_app, db
from app.models import Admin, Book, Student, Inventory, ReadBook

app = create_app()

# Register CLI context: these objects will be auto-loaded when running "flask shell".
@app.shell_context_processor
def make_shell_context():
    return {
        'app': app,
        'db': db,
        'Admin': Admin,
        'Book': Book,
        'Student': Student,
        'Inventory': Inventory,
        'ReadBook': ReadBook
    }

if __name__ == '__main__':
    app.run()