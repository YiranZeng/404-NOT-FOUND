from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import main
from .forms import (
    Login,
    SearchBookForm,
    ChangePasswordForm,
    EditInfoForm,
    SearchStudentForm,
    NewStoreForm,
    StoreForm,
    BorrowForm,
)
from .. import db
from ..models import Admin, Book, Inventory, Student, ReadBook
import time, datetime


@main.route('/', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = Admin.query.filter_by(
            admin_id=form.account.data, password=form.password.data
        ).first()
        if user is None:
            flash('Invalid account or password!')
            return redirect(url_for('.login'))
        else:
            login_user(user)
            session['admin_id'] = user.admin_id
            session['name'] = user.admin_name
            return redirect(url_for('.index'))
    return render_template('main/login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('.login'))


@main.route('/index')
@login_required
def index():
    return render_template('main/index.html', name=session.get('name'))


@main.route('/echarts')
@login_required
def echarts():
    days = []
    num = []
    today_date = datetime.date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    ten_ago = int(today_stamp) - 9 * 86400
    for i in range(0, 10):
        borr = ReadBook.query.filter_by(start_date=str((ten_ago + i * 86400) * 1000)).count()
        retu = ReadBook.query.filter_by(end_date=str((ten_ago + i * 86400) * 1000)).count()
        num.append(borr + retu)
        days.append(timeStamp((ten_ago + i * 86400) * 1000))
    data = []
    for i in range(0, 10):
        item = {'name': days[i], 'num': num[i]}
        data.append(item)
    return jsonify(data)


@main.route('/user/<id>')
@login_required
def user_info(id):
    user = Admin.query.filter_by(admin_id=id).first()
    return render_template('main/user-info.html', user=user, name=session.get('name'))


@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.password2.data != form.password.data:
        flash('The two passwords do not match!')
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Password successfully changed!')
            return redirect(url_for('.index'))
        else:
            flash('Original password is incorrect. Change failed!')
    return render_template("main/change-password.html", form=form)


@main.route('/change_info', methods=['GET', 'POST'])
@login_required
def change_info():
    form = EditInfoForm()
    if form.validate_on_submit():
        current_user.admin_name = form.name.data
        db.session.add(current_user)
        flash('Personal information updated successfully!')
        return redirect(url_for('.user_info', id=current_user.admin_id))
    form.name.data = current_user.admin_name
    id = current_user.admin_id
    right = current_user.right
    return render_template('main/change-info.html', form=form, id=id, right=right)


@main.route('/search_book', methods=['GET', 'POST'])
@login_required
def search_book():  # No submit handling here; use Ajax for partial refresh
    form = SearchBookForm()
    return render_template('main/search-book.html', name=session.get('name'), form=form)


@main.route('/books', methods=['POST'])
def find_book():
    # Get the search content and selected search method from the form
    search_content = request.form.get('content', '').strip()
    search_method = request.form.get('method')

    # If the search box is empty, return ALL books
    if not search_content:
        books = Book.query.all()
    else:
        # Otherwise, filter books based on the selected search method
        if search_method == 'book_name':
            books = Book.query.filter(Book.book_name.like(f'%{search_content}%')).all()
        elif search_method == 'author':
            books = Book.query.filter(Book.author.like(f'%{search_content}%')).all()
        elif search_method == 'class_name':
            books = Book.query.filter(Book.class_name.like(f'%{search_content}%')).all()
        elif search_method == 'isbn':
            books = Book.query.filter(Book.isbn.like(f'%{search_content}%')).all()
        else:
            books = []

    # Build a JSON-friendly list of book data
    data = []
    for book in books:
        count = Inventory.query.filter_by(isbn=book.isbn).count()       # total copies
        available = Inventory.query.filter_by(isbn=book.isbn, status=True).count()  # available copies

        data.append({
            'isbn': book.isbn,
            'book_name': book.book_name,
            'press': book.press,
            'author': book.author,
            'class_name': book.class_name,
            'count': count,
            'available': available
        })

    # Return data as JSON (used by AJAX on the front end)
    return jsonify(data)



@main.route('/user/book', methods=['GET', 'POST'])
def user_book():
    form = SearchBookForm()
    return render_template('main/user-book.html', form=form)


@main.route('/search_student', methods=['GET', 'POST'])
@login_required
def search_student():
    form = SearchStudentForm()
    return render_template('main/search-student.html', name=session.get('name'), form=form)


def timeStamp(timeNum):
    if timeNum is None:
        return timeNum
    else:
        timeStamp = float(float(timeNum) / 1000)
        timeArray = time.localtime(timeStamp)
        print(time.strftime("%Y-%m-%d", timeArray))
        return time.strftime("%Y-%m-%d", timeArray)



def calc_student_fine(card_id, rate_per_day=1.0):
    now_ts = int(time.time())
    total_fine = 0.0

    records = ReadBook.query.filter_by(card_id=card_id).all()

    for r in records:
        if r.end_date is None:
            try:
                due_ts = int(r.due_date) // 1000
            except (TypeError, ValueError):
                continue

            overdue_days = (now_ts - due_ts) // 86400
            grace = 30
            if overdue_days > grace:
                charge_days = overdue_days - grace
                total_fine += charge_days * rate_per_day

    return round(total_fine, 2)

@main.route('/student', methods=['POST'])
def find_student():
    card = request.form.get('card')
    password = request.form.get('password')

    stu = Student.query.filter_by(card_id=card, password=password).first()

    if stu is None:
        return jsonify([])

    total_fine = calc_student_fine(stu.card_id)

    stu.debt = total_fine > 0
    db.session.add(stu)
    db.session.commit()

    valid_date = timeStamp(stu.valid_date)
    return jsonify([{
        'name': stu.student_name,
        'gender': stu.sex,
        'valid_date': valid_date,
        'debt': stu.debt,
        'fine': total_fine 
    }])


@main.route('/record', methods=['POST'])
def find_record():
    card = request.form.get('card')
    password = request.form.get('password')

    stu = Student.query.filter_by(card_id=card, password=password).first()
    if stu is None:
        return jsonify([])

    records = (
        db.session.query(ReadBook)
        .join(Inventory)
        .join(Book)
        .filter(ReadBook.card_id == card)
        .with_entities(
            ReadBook.barcode,
            Inventory.isbn,
            Book.book_name,
            Book.author,
            ReadBook.start_date,
            ReadBook.end_date,
            ReadBook.due_date,
        )
        .all()
    )

    now_ts = int(time.time())
    rate_per_day = 1.0

    data = []
    for record in records:
        start_date = timeStamp(record.start_date)
        due_date = timeStamp(record.due_date)
        end_date = timeStamp(record.end_date)

        # 计算单本书罚金
        fine = 0.0
        if record.end_date is None:
            try:
                due_ts = int(record.due_date) // 1000
                overdue_days = (now_ts - due_ts) // 86400
                if overdue_days > 0:
                    fine = round(overdue_days * rate_per_day, 2)
            except (TypeError, ValueError):
                pass

        if end_date is None:
            end_date = 'Not returned'

        item = {
            'barcode': record.barcode,
            'book_name': record.book_name,
            'author': record.author,
            'start_date': start_date,
            'due_date': due_date,
            'end_date': end_date,
            'fine': fine        
        }
        data.append(item)
    return jsonify(data)


@main.route('/user/student', methods=['GET', 'POST'])
def user_student():
    form = SearchStudentForm()
    return render_template('main/user-student.html', form=form)


@main.route('/storage', methods=['GET', 'POST'])
@login_required
def storage():
    form = StoreForm()
    if form.validate_on_submit():
        book = Book.query.filter_by(isbn=request.form.get('isbn')).first()
        exist = Inventory.query.filter_by(barcode=request.form.get('barcode')).first()
        if book is None:
            flash(
                'Add failed. Please ensure the book info has been recorded. If not, add it in "New Book Registration".')
        else:
            if len(request.form.get('barcode')) != 6:
                flash('Book code length error')
            else:
                if exist is not None:
                    flash('This barcode already exists!')
                else:
                    item = Inventory()
                    item.barcode = request.form.get('barcode')
                    item.isbn = request.form.get('isbn')
                    item.admin = current_user.admin_id
                    item.location = request.form.get('location')
                    item.status = True
                    item.withdraw = False
                    item.storage_date = datetime.datetime.now()
                    db.session.add(item)
                    db.session.commit()
                    flash('Stored successfully!')
        return redirect(url_for('.storage'))
    return render_template('main/storage.html', name=session.get('name'), form=form)


@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    form = NewStoreForm()
    if form.validate_on_submit():
        if len(request.form.get('isbn')) != 13:
            flash('ISBN length error')
        else:
            exist = Book.query.filter_by(isbn=request.form.get('isbn')).first()
            if exist is not None:
                flash('This book already exists. Please verify before adding again, or use the storage form.')
            else:
                book = Book()
                book.isbn = request.form.get('isbn')
                book.book_name = request.form.get('book_name')
                book.press = request.form.get('press')
                book.author = request.form.get('author')
                book.class_name = request.form.get('class_name')
                db.session.add(book)
                db.session.commit()
                flash('Book information added successfully!')
        return redirect(url_for('.new_store'))
    return render_template('main/new-store.html', name=session.get('name'), form=form)


@main.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    form = BorrowForm()
    return render_template('main/borrow.html', name=session.get('name'), form=form)


@main.route('/find_stu_book', methods=['GET', 'POST'])
def find_stu_book():
    try:
        card = request.form.get('card')
        title = request.form.get('book_name', '').strip()
        print(f"DEBUG: card = {card}, title = {title}")

        stu = Student.query.filter_by(card_id=card).first()
        if not stu:
            print("DEBUG: Student not found")
            return jsonify([{'stu': 0}])

        # ---------- Safe conversion valid_date ----------
        valid_ts = 0
        if stu.valid_date:
            try:
                # If it is a numeric timestamp (milliseconds)
                if isinstance(stu.valid_date, (int, float)):
                    valid_ts = stu.valid_date / 1000
                # If it is a string number (e.g., ‘1725148800000’)
                elif isinstance(stu.valid_date, str) and stu.valid_date.isdigit():
                    valid_ts = int(stu.valid_date) / 1000
                # If it is a datetime object
                else:
                    valid_ts = stu.valid_date.timestamp()
            except Exception as e:
                print("Date parse error:", e)
                valid_ts = 0

        now_ts = time.time()
        print(f"DEBUG: valid_ts = {valid_ts}, now_ts = {now_ts}")

        # ---------- Status Check ----------
        if stu.debt:
            print("DEBUG: The student has outstanding fees.")
            return jsonify([{'stu': 1}])
        if valid_ts and valid_ts < now_ts:
            print("DEBUG: The card has expired.")
            return jsonify([{'stu': 2}])
        if stu.loss:
            print("DEBUG: The card has been reported lost.")
            return jsonify([{'stu': 3}])

        # ---------- Search for Books ----------
        query = (
            db.session.query(Book)
            .join(Inventory)
            .filter(Inventory.status.is_(True))
        )

        if title:
            query = query.filter(Book.book_name.ilike(f"%{title}%"))

        books = query.with_entities(
            Inventory.barcode, Book.isbn, Book.book_name, Book.author, Book.press
        ).all()

        print(f"DEBUG: Number of books found = {len(books)}")

        data = [
            {
                'barcode': b.barcode,
                'isbn': b.isbn,
                'book_name': b.book_name,
                'author': b.author,
                'press': b.press
            }
            for b in books
        ]

        return jsonify(data)

    except Exception as e:
        print("ERROR:", e)
        import traceback;
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@main.route('/out', methods=['GET', 'POST'])
@login_required
def out():
    today_date = datetime.date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    barcode = request.args.get('barcode')
    card = request.args.get('card')
    book_name = request.args.get('book_name')
    readbook = ReadBook()
    readbook.barcode = barcode
    readbook.card_id = card
    readbook.start_date = int(today_stamp) * 1000
    readbook.due_date = (int(today_stamp) + 40 * 86400) * 1000
    readbook.borrow_admin = current_user.admin_id
    db.session.add(readbook)
    db.session.commit()
    book = Inventory.query.filter_by(barcode=barcode).first()
    book.status = False
    db.session.add(book)
    db.session.commit()
    bks = (
        db.session.query(Book)
        .join(Inventory)
        .filter(Book.book_name.contains(book_name), Inventory.status == 1)
        .with_entities(Inventory.barcode, Book.isbn, Book.book_name, Book.author, Book.press)
        .all()
    )
    data = []
    for bk in bks:
        item = {
            'barcode': bk.barcode,
            'isbn': bk.isbn,
            'book_name': bk.book_name,
            'author': bk.author,
            'press': bk.press
        }
        data.append(item)
    return jsonify({
    "status": "ok",
    "msg": "Borrow successful!",
    "data": data
})


@main.route('/return', methods=['GET', 'POST'])
@login_required
def return_book():
    form = SearchStudentForm()
    return render_template('main/return.html', name=session.get('name'), form=form)


@main.route('/find_not_return_book', methods=['GET', 'POST'])
def find_not_return_book():
    stu = Student.query.filter_by(card_id=request.form.get('card')).first()
    today_date = datetime.date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    if stu is None:
        return jsonify([{'stu': 0}])  # not found
    #if stu.debt is True:
       # return jsonify([{'stu': 1}])  # has outstanding fees
    if int(stu.valid_date) < int(today_stamp) * 1000:
        return jsonify([{'stu': 2}])  # expired
    if stu.loss is True:
        return jsonify([{'stu': 3}])  # reported lost
    books = (
        db.session.query(ReadBook)
        .join(Inventory)
        .join(Book)
        .filter(
            ReadBook.card_id == request.form.get('card'),
            ReadBook.end_date.is_(None)
        )
        .with_entities(
            ReadBook.barcode, Book.isbn, Book.book_name, ReadBook.start_date, ReadBook.due_date
        )
        .all()
    )
    data = []
    for book in books:
        start_date = timeStamp(book.start_date)
        due_date = timeStamp(book.due_date)
        item = {
            'barcode': book.barcode,
            'isbn': book.isbn,
            'book_name': book.book_name,
            'start_date': start_date,
            'due_date': due_date
        }
        data.append(item)
    return jsonify(data)


@main.route('/in', methods=['GET', 'POST'])
@login_required
def bookin():
    barcode = request.args.get('barcode')
    card = request.args.get('card')
    record = ReadBook.query.filter(
        ReadBook.barcode == barcode,
        ReadBook.card_id == card,
        ReadBook.end_date.is_(None)
    ).first()
    today_date = datetime.date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    record.end_date = int(today_stamp) * 1000
    record.return_admin = current_user.admin_id
    db.session.add(record)
    db.session.commit()
    book = Inventory.query.filter_by(barcode=barcode).first()
    book.status = True
    db.session.add(book)
    db.session.commit()
    bks = (
        db.session.query(ReadBook)
        .join(Inventory)
        .join(Book)
        .filter(ReadBook.card_id == card, ReadBook.end_date.is_(None))
        .with_entities(
            ReadBook.barcode, Book.isbn, Book.book_name, ReadBook.start_date, ReadBook.due_date
        )
        .all()
    )
    data = []
    for bk in bks:
        start_date = timeStamp(bk.start_date)
        due_date = timeStamp(bk.due_date)
        item = {
            'barcode': bk.barcode,
            'isbn': bk.isbn,
            'book_name': bk.book_name,
            'start_date': start_date,
            'due_date': due_date
        }
        data.append(item)
    return jsonify({
    "status": "ok",
    "msg": "Return successful!",
    "data": data
})


@main.route('/delete_book', methods=['GET', 'POST'])
@login_required
def delete_book():
    isbn = request.args.get('isbn') or request.form.get('isbn')
    books = []

    # If the user enters an ISBN, search for all copies.
    if isbn:
        books = (
            db.session.query(Inventory)
            .join(Book, Inventory.isbn == Book.isbn)
            .filter(Inventory.isbn == isbn)
            .with_entities(
                Inventory.barcode,
                Book.isbn,
                Book.book_name,
                Book.author,
                Book.press,
                Inventory.location
            )
            .all()
        )

    # Processing deletion requests
    if request.method == 'POST' and 'selected_books' in request.form:
        selected = request.form.getlist('selected_books')  # barcode list
        if not selected:
            flash('Please select at least one copy to delete.')
            return redirect(url_for('.delete_book'))

        try:
            for barcode in selected:
                Inventory.query.filter_by(barcode=barcode).delete()
            db.session.commit()
            flash(f"Successfully deleted {len(selected)} book copy/copies.")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting books: {e}")
        return redirect(url_for('.delete_book'))

    return render_template('main/delete-book.html', name=session.get('name'), books=books)






@main.route('/admin/student', methods=['POST'])
@login_required
def admin_find_student():
    card = request.form.get('card')
    stu = Student.query.filter_by(card_id=card).first()
    if stu is None:
        return jsonify([])

    total_fine = calc_student_fine(stu.card_id)
    stu.debt = total_fine > 0
    db.session.add(stu)
    db.session.commit()

    valid_date = timeStamp(stu.valid_date)
    return jsonify([{
        'name': stu.student_name,
        'gender': stu.sex,
        'valid_date': valid_date,
        'debt': stu.debt
    }])


@main.route('/admin/record', methods=['POST'])
@login_required
def admin_find_record():
    card = request.form.get('card')

    records = (
        db.session.query(ReadBook)
        .join(Inventory)
        .join(Book)
        .filter(ReadBook.card_id == card)
        .with_entities(
            ReadBook.barcode,
            Inventory.isbn,
            Book.book_name,
            Book.author,
            ReadBook.start_date,
            ReadBook.end_date,
            ReadBook.due_date,
        )
        .all()
    )

    data = []
    for record in records:
        start_date = timeStamp(record.start_date)
        due_date = timeStamp(record.due_date)
        end_date = timeStamp(record.end_date)
        if end_date is None:
            end_date = 'Not returned'
        item = {
            'barcode': record.barcode,
            'book_name': record.book_name,
            'author': record.author,
            'start_date': start_date,
            'due_date': due_date,
            'end_date': end_date
        }
        data.append(item)
    return jsonify(data)

