from sqlalchemy import Column, String, Integer, Float, Text, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class Genre(Base):

    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Book(Base):

    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String(30), nullable=False)
    publisher = Column(String(25))
    genre = Column(Integer, ForeignKey(Genre.id))
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    picture = Column(String, nullable=False)
    # created = Column(String, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'genre': self.genre,
            'price': self.price,
            'description': self.description,
            'picture': self.picture
        }

engine = create_engine('postgresql://catalog:milkandcream@localhost/catalog')
Base.metadata.create_all(engine)
