from config import LINK
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship


engine = create_engine(LINK)
Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'
    users_id = Column(Integer, primary_key=True, autoincrement=True)
    lastname = Column(String(100), nullable=False)
    firstname = Column(String(100), nullable=False)
    middlename = Column(String(100))
    login = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)


class Abonements(Base):
    __tablename__ = 'abonements'
    abonement_id = Column(Integer, primary_key=True, autoincrement=True)
    data_start = Column(Date, nullable=False, default=datetime.utcnow)
    data_finish = Column(Date, nullable=False)
    visitors_id = Column(Integer, ForeignKey('visitors.visitors_id'), nullable=False)
    books_id = Column(Integer, ForeignKey('books.books_id'), nullable=False)


class Visitors(Base):
    __tablename__ = 'visitors'
    visitors_id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String(200), nullable=False)
    date_of_birthday = Column(Date, nullable=False)


class Books(Base):
    __tablename__ = 'books'
    books_id = Column(Integer, primary_key=True, autoincrement=True)
    name_book = Column(String(200), nullable=False)
    authors_id = Column(Integer, ForeignKey('authors.authors_id'), nullable=False)
    edition = Column(String(100), nullable=False)


class Authors(Base):
    __tablename__ = 'authors'
    authors_id = Column(Integer, primary_key=True, autoincrement=True)
    fullname_author = Column(String(200), nullable=False)

Base.metadata.create_all(engine)


def check_password(username, password):
    user = session.query(Users).filter_by(login=username).first()
    if user and user.password == password:
        return True
    return False


def create_user(last_name, first_name, middle_name, username, email, password):
    if session.query(Users).filter_by(login=username).first():
        return False
    user = Users(lastname=last_name, firstname=first_name, middlename=middle_name, login=username, email=email, password=password)
    session.add(user)
    session.commit()
    return True


def get_author(authors_id):
    return session.query(Authors).filter_by(authors_id=authors_id).first()


def get_all_authors():
    return session.query(Authors).all()


def get_all_books():
    return session.query(Books).all()


def get_all_visitors():
    return session.query(Visitors).all()


def get_all_users():
    return session.query(Users).all()


def get_all_abonements():
    return session.query(Abonements).all()


def create_abonement(data_finish, visitors_id, books_id):
    abonement = Abonements(data_finish=data_finish, visitors_id=visitors_id, books_id=books_id)
    session.add(abonement)
    session.commit()


def create_visitor(fullname, date_of_birthday):
    visitor = Visitors(fullname=fullname, date_of_birthday=date_of_birthday)
    session.add(visitor)
    session.commit()


def create_book(name_book, authors_id, edition):
    book = Books(name_book=name_book, authors_id=authors_id, edition=edition)
    session.add(book)
    session.commit()


def create_author(fullname_author):
    author = Authors(fullname_author=fullname_author)
    session.add(author)
    session.commit()


def edit_book(books_id, name_book, authors_id, edition):
    book = session.query(Books).filter_by(books_id=books_id).first()
    book.name_book = name_book
    book.authors_id = authors_id
    book.edition = edition
    session.commit()


def delete_book(books_id):
    book = session.query(Books).filter_by(books_id=books_id).first()
    session.delete(book)
    session.commit()


def edit_author(authors_id, fullname_author):
    author = session.query(Authors).filter_by(authors_id=authors_id).first()
    author.fullname_author = fullname_author
    session.commit()


def delete_author(authors_id):
    author = session.query(Authors).filter_by(authors_id=authors_id).first()
    session.delete(author)
    session.commit()


def get_book(books_id):
    return session.query(Books).filter_by(books_id=books_id).first()


def get_author(authors_id):
    return session.query(Authors).filter_by(authors_id=authors_id).first()
