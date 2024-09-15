import random
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from flask_mail import Mail, Message
from functools import wraps
from config import SECRET, SMTP_USER, SMTP_PASS, SMTP_PORT, SMTP_HOST, MAIL_USE_TLS
from db import (
    check_password, create_user, get_all_users,
    get_all_abonements, get_all_authors, get_author,
    get_all_visitors, get_all_books, get_book,
    create_author, create_book, create_abonement,
    create_visitor, edit_book, edit_author,
    delete_book, delete_author
)
import pandas as pd


app = Flask(__name__)


def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))


@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data['email']
    verification_code = generate_verification_code()
    session['verification_code'] = verification_code
    session['email'] = email
    msg = Message('Код подтверждения', recipients=[email])
    msg.body = f'Ваш код подтверждения: {verification_code}'
    try:
        mail.send(msg)
        return jsonify({'message': 'Код отправлен'}), 200
    except Exception as e:
        return jsonify({'message': 'Ошибка отправки кода'}), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        last_name = request.form['lastName']
        first_name = request.form['firstName']
        middle_name = request.form['middleName']
        username = request.form['username']
        email = request.form['email']
        verification_code = request.form['verificationCode']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        if password != confirm_password:
            flash('Пароли не совпадают!')
            return redirect(url_for('register'))
        if verification_code != session.get('verification_code'):
            flash('Неправильный код подтверждения!')
            return redirect(url_for('register'))
        if email != session.get('email'):
            flash('Почта не совпадает с введенной ранее!')
            return redirect(url_for('register'))
        if create_user(last_name, first_name, middle_name, username, email, password):
            flash('Регистрация успешна! Теперь вы можете войти.')
            return redirect(url_for('users'))
        else:
            flash('Логин уже занят!')
            return redirect(url_for('register'))
    return render_template('register.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_password(username, password):
            session['username'] = username
            flash('Вы успешно вошли в систему!')
            return redirect(url_for('users'))
        else:
            flash('Неверный логин или пароль!')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Вы вышли из системы.')
    return redirect(url_for('login'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    return render_template("users.html", data=get_all_users())


@app.route('/visitors', methods=['GET', 'POST'])
@login_required
def visitors():
    return render_template("visitors.html", data=get_all_visitors())


@app.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    books = get_all_books()
    authors = get_all_authors()
    return render_template('books.html', data=books, authors=authors)


@app.route('/authors', methods=['GET', 'POST'])
@login_required
def authors():
    return render_template("authors.html", data=get_all_authors())


@app.route('/abonements', methods=['GET', 'POST'])
@login_required
def abonements():
    abonements = get_all_abonements()
    visitors = get_all_visitors()
    books = get_all_books()
    return render_template('abonements.html', data=abonements, visitors=visitors, books=books)


@app.route('/edit_book_route', methods=['GET', 'POST'])
@login_required
def edit_book_route():
    books_id = request.form['books_id']
    book = get_book(books_id)
    authors = get_all_authors()
    return render_template('edit_book.html', book=book, authors=authors)


@app.route('/change_book_route', methods=['GET', 'POST'])
@login_required
def change_book_route():
    books_id = request.form['books_id']
    name_book = request.form['new_name_book']
    authors_id = request.form['new_authors_id']
    edition = request.form['new_edition']
    edit_book(books_id, name_book, authors_id, edition)
    return redirect(url_for('books'))


@app.route('/delete_book_route', methods=['GET', 'POST'])
@login_required
def delete_book_route():
    books_id = request.form['books_id']
    delete_book(books_id)
    return redirect(url_for('books'))


@app.route('/create_abonement_route', methods=['GET', 'POST'])
@login_required
def create_abonement_route():
    data_finish = request.form['data_finish']
    visitors_id = request.form['visitors_id']
    books_id = request.form['books_id']
    create_abonement(data_finish, visitors_id, books_id)
    return redirect(url_for('abonements'))


@app.route('/create_visitor_route', methods=['GET', 'POST'])
@login_required
def create_visitor_route():
    fullname = request.form['fullname']
    date_of_birthday = request.form['date_of_birthday']
    create_visitor(fullname, date_of_birthday)
    return redirect(url_for('visitors'))


@app.route('/create_book_route', methods=['GET', 'POST'])
@login_required
def create_book_route():
    name_book = request.form['name_book']
    authors_id = request.form['authors_id']
    edition = request.form['edition']
    create_book(name_book, authors_id, edition)
    return redirect(url_for('books'))


@app.route('/create_author_route', methods=['GET', 'POST'])
@login_required
def create_author_route():
    fullname_author = request.form['fullname_author']
    create_author(fullname_author)
    return redirect(url_for('authors'))


@app.route('/edit_author_route', methods=['GET', 'POST'])
@login_required
def edit_author_route():
    authors_id = request.form['authors_id']
    author = get_author(authors_id)
    return render_template('edit_author.html', author=author)


@app.route('/change_author_route', methods=['GET', 'POST'])
@login_required
def change_author_route():
    authors_id = request.form['authors_id']
    authors_fullname = request.form['new_fullname_author']
    edit_author(authors_id, authors_fullname)
    return redirect(url_for('authors'))


@app.route('/delete_author_route', methods=['GET', 'POST'])
@login_required
def delete_author_route():
    authors_id = request.form['authors_id']
    delete_author(authors_id)
    return redirect(url_for('authors'))


@app.route('/export_books_csv', methods=['GET'])
@login_required
def export_books_csv():
    books = get_all_books()
    books_dict = [{'books_id': book.books_id, 'name_book': book.name_book,
                   'authors_id': book.authors_id, 'edition': book.edition} for book in books]
    df = pd.DataFrame(books_dict)
    csv_data = df.to_csv(index=False, header=['Ключ', 'Название книги', 'ID автора', 'Издание'], encoding='utf-8')
    headers = {
        'Content-Disposition': 'attachment; filename=books.csv',
        'Content-Type': 'text/csv',
    }
    return Response(csv_data, headers=headers)


@app.route('/export_authors_csv', methods=['GET'])
@login_required
def export_authors_csv():
    authors = get_all_authors()
    authors_dict = [{'authors_id': author.authors_id, 'fullname_author': author.fullname_author} for author in authors]
    df = pd.DataFrame(authors_dict)
    csv_data = df.to_csv(index=False, header=['Ключ', 'Имя автора'], encoding='utf-8')
    headers = {
        'Content-Disposition': 'attachment; filename=authors.csv',
        'Content-Type': 'text/csv',
    }
    return Response(csv_data, headers=headers)


@app.route('/export_abonements_csv', methods=['GET'])
@login_required
def export_abonements_csv():
    abonements = get_all_abonements()
    abonements_dict = [{'abonement_id': abonement.abonement_id, 'data_start': abonement.data_start,
                        'data_finish': abonement.data_finish, 'visitors_id': abonement.visitors_id,
                        'books_id': abonement.books_id} for abonement in abonements]
    df = pd.DataFrame(abonements_dict)
    csv_data = df.to_csv(index=False, header=['Ключ', 'Дата получения', 'Дата сдачи', 'ID посетителя', 'ID книги'], encoding='utf-8')
    headers = {
        'Content-Disposition': 'attachment; filename=abonements.csv',
        'Content-Type': 'text/csv',
    }
    return Response(csv_data, headers=headers)


@app.route('/export_users_csv', methods=['GET'])
@login_required
def export_users_csv():
    users = get_all_users()
    users_dict = [{'users_id': user.users_id, 'lastname': user.lastname,
                        'firstname': user.firstname, 'middlename': user.middlename,
                        'login': user.login, 'email': user.email} for user in users]
    df = pd.DataFrame(users_dict)
    csv_data = df.to_csv(index=False, header=['Ключ', 'Фамилия', 'Имя', 'Отчество', 'Логин', 'Почта'], encoding='utf-8')
    headers = {
        'Content-Disposition': 'attachment; filename=users.csv',
        'Content-Type': 'text/csv',
    }
    return Response(csv_data, headers=headers)


@app.route('/export_visitors_csv', methods=['GET'])
@login_required
def export_visitors_csv():
    visitors = get_all_visitors()
    visitors_dict = [{'visitors_id': visitor.visitors_id, 'fullname': visitor.fullname,
                        'date_of_birthday': visitor.date_of_birthday} for visitor in visitors]
    df = pd.DataFrame(visitors_dict)
    csv_data = df.to_csv(index=False, header=['Ключ', 'ФИО', 'Дата рождения'], encoding='utf-8')
    headers = {
        'Content-Disposition': 'attachment; filename=visitors.csv',
        'Content-Type': 'text/csv',
    }
    return Response(csv_data, headers=headers)


if __name__ == '__main__':
    app.secret_key = SECRET
    app.config['MAIL_SERVER'] = SMTP_HOST
    app.config['MAIL_PORT'] = SMTP_PORT
    app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = SMTP_USER
    app.config['MAIL_PASSWORD'] = SMTP_PASS
    app.config['MAIL_DEFAULT_SENDER'] = SMTP_USER
    mail = Mail(app)
    app.run(debug=False)
