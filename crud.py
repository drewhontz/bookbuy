from db_config import Base, Genre, Book
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://catalog:milkandcream@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def show_books(gid):
    return session.query(Book).filter_by(genre=gid).all()


def get_book_by_id(bid):
    return session.query(Book).filter_by(id=bid).one()


def show_genres():
    return session.query(Genre).all()


def get_genre_by_id(gid):
    res = session.query(Genre).filter_by(id=gid).first()
    return res


def show_latest():
    return session.query(Book).limit(5)


def show_catalog():
    return session.query(Book).all()


def add_genre(name):
    g = Genre(name=name)
    session.add(g)
    session.commit()


def edit_genre(gid, name):
    g = get_genre_by_id(gid)
    g.name = name
    session.add(g)
    session.commit()


def delete_genre(gid):
    session.delete(get_genre_by_id(gid))
    session.commit()


def delete_book(bid):
    session.delete(get_book_by_id(bid))
    session.commit()


def add_book(title, author, publisher, price, description, picture, genre_id):
    b = Book(title=title, author=author, publisher=publisher, price=price,
             description=description, picture=picture, genre=genre_id)
    session.add(b)
    session.commit()


def edit_book(bid, title, author, publisher, price, description, picture,
              genre_id):
    b = get_book_by_id(bid)

    b.title = title
    b.author = author
    b.publisher = publisher
    b.price = price
    b.description = description
    b.picture = picture
    b.genre = genre_id

    session.add(b)
    session.commit()
