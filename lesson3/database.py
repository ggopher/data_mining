from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
import sqlalchemy as db

engine = create_engine('sqlite:///gb_blog.db')
models.Base.metadata.create_all(bind=engine)

SessionMaker = sessionmaker(bind=engine)



# def get_db():
#     db =SessionMaker()
#     try:
#         yield db
#     finally:
#         db.close()


if __name__ == '__main__':
    db = SessionMaker()
    print(1)


"""
Post
id = Column(Integer, autoincrement=True, primary_key=True)
url = Column(String, unique=True, nullable=False)
img_url = Column(String, unique=False, nullable=True)
author_id = Column(Integer, ForeignKey('writer.id'))
writer = relationship("Writer", back_populates='posts')
tag = relationship('Tag', secondary=tag_post, back_populates='posts')

Writer
id = Column(Integer, autoincrement=True, primary_key=True)
name = Column(String, unique=False, nullable=False)
url = Column(String, unique=True, nullable=False)
posts = relationship("Post")

Tag
id = Column(Integer, autoincrement=True, primary_key=True)
name = Column(String, unique=False, nullable=False)
url = Column(String, unique=True, nullable=False)
posts = relationship('Post', secondary=tag_post)
"""

# writer = models.Writer(name='Writer 1', url='sdfsdgsgsdgwer23')
# tags = models.Tag(name='привет', url='sdfsdgsgsdgwer23')
# tags_posts = models.Base
# post = models.Post(url='sdfsdgsgsdgwer23', img_url='sdfsdfsdf', writer=writer)
# db.add(post)
# db.add(writer)
# db.commit()

print(1)
# db.select([author]).where(author.columns.url == 'https://geekbrains.ru/users/3899893')
# query = db.select([author])
# ResultProxy = connection.execute(query)
# ResultSet = ResultProxy.fetchall()
db.close()