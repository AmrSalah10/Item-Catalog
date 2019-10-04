from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Movie

engine = create_engine('sqlite:///movies.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Category 1
Category1 = Category(name="Romance")

session.add(Category1)
session.commit()

movie1 = Movie(name="Titanic", story="The movie is about"
               "the 1912 sinking of the RMS Titanic. It stars Kate Winslet"
               "and Leonardo DiCaprio. The two play characters who are of"
               "different social classes. They fall in love after"
               "meeting aboard the ship, but it was not good for a rich girl"
               "to fall in love with a poor boy in 1912",
               category=Category1, IMDB_Rating='95%')

session.add(movie1)
session.commit()


movie2 = Movie(name="Notebook", story="The notebook is a drama film"
               "produced in the United States and released in 2004."
               "Starring Ryan Gosling, Rachel McAdams, James Garner,"
               "Gina Rowlands and Joan Alle",
               category=Category1)

session.add(movie2)
session.commit()


# Category 2
Category2 = Category(name="Action")

session.add(Category2)
session.commit()

movie1 = Movie(name="Mission Imposible", category=Category2)

session.add(movie1)
session.commit()


movie2 = Movie(name="Taken", category=Category2)

session.add(movie2)
session.commit()


# Category 3
Category3 = Category(name="Horror")

session.add(Category3)
session.commit()

movie1 = Movie(name="The Ring", category=Category3)

session.add(movie1)
session.commit()


movie2 = Movie(name="IT", category=Category3)

session.add(movie2)
session.commit()


print("Done!")
