import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)


class User(Base):
    __tablename__ = 'user'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    picture = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

    # Show Movie data in json
    @property
    def serialize(self):
        return {
                'name': self.name,
                'id': self.id,
                'email': self.email,
                'user_id': self.user_id,
                }


class Movie(Base):
    __tablename__ = 'movie'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    story = Column(String(800))
    IMDB_Rating = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Show Movie data in json
    @property
    def serialize(self):
        return {
                'name': self.name,
                'id': self.id,
                'story': self.story,
                'IMDB_Rating': self.IMDB_Rating,
                }


engine = create_engine('sqlite:///movies.db')
Base.metadata.create_all(engine)
