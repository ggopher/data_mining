"""
Homework data mining Lesson 3
Kaltakhchan Karen

Источник https://geekbrains.ru/posts/
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:

url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
список тегов
реализовать SQL структуру хранения данных c следующими таблицами

Post
Comment
Writer
Tag
Организовать реляционные связи между таблицами

При сборе данных учесть, что полученый из данных автор уже может быть в БД и значит необходимо это заблаговременно проверить.
Не забываем закрывать сессию по завершению работы с ней
"""

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urlparse
import time
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from dateutil import parser as date_parser

#Заходим на страницу, получаем список постов, заходим на следующую и так далее
class MagnitParser:
    _headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    }
    _params = {
        'geo': 'moskva',
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)
        self._root_url = f'{self._url.scheme}://{self._url.hostname}'
        mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = mongo_client['magnit']

    def _get_soup(self, url: str):
        response = requests.get(url, headers=self._headers, params=self._params)
        return BeautifulSoup(response.text, 'lxml')

    def get_links(self):
        #Здесь можно переписать, в один заход.
        soup = self._get_soup(self.start_url)
        print(f"Collecting posts url's on {self.start_url}")
        posts_links = []
        page_count = int(soup.find('ul', attrs={'class': 'gb__pagination'}).contents[-2].text)
        # for i in range(page_count-1):         # DO UNTILL immitation
        for i in range(1):  # DO UNTILL immitation
            time.sleep(0.1)
            posts_list_div = soup.find('div', attrs={'class': 'post-items col-md-8 col-sm-12 col-xs-12'})
            for post_link in posts_list_div.findChildren('a', attrs={'class': 'post-item__title h3 search_text'}):
                posts_links.append(self._root_url + post_link.attrs.get('href'))
            #Pagination block
            next_page = self._root_url + soup.find_all("a", attrs={'rel': 'next'})[-1].attrs.get('href')
            soup = self._get_soup(next_page)
            print(f"Collecting posts url's on {next_page}")
                # print(next_page + 'parsed')
        #   print(i)
        return posts_links
        # print(1)

    def parse(self):
        posts_links = self.get_links()
        print(posts_links)
        self.db_init()
        for post_url in posts_links:
            post_soup = self._get_soup(post_url)
            post_data = self.get_post_structure(post_soup, post_url)
            post_data['comments'] = self.get_post_comments(post_soup)

            for i, key in post_data.items():
                print(f'{i}: {key}')
            self.commit_to_db(post_data)
            # print(post_data)
            # self.save_to(product_data)
            print('Post parsed')
        self.db_close()



    def get_post_structure(self, post_soup, url):
        print('POST PARSING BEGIN')

        post_template = {
            'post_title': lambda soup: soup.find('h1', attrs={'class': 'blogpost-title text-left text-dark m-t-sm'}).text
            ,'post_publish_date': lambda soup: date_parser.parse(soup.find('time', attrs={'class': 'text-md text-muted m-r-md'})['datetime'])
            ,'image_url': lambda soup: soup.find('img')['src']
            ,'author': lambda soup: soup.find('div', attrs={'itemprop': 'author'}).text
            ,'author_url': lambda soup: f"{self._root_url}{soup.find('div', attrs={'itemprop': 'author'}).parent.attrs.get('href')}"
            ,'post_tags': lambda soup: [tag.text for tag in soup.find_all('a', attrs={'class': 'small'})]
        }
        post = {'url': url}
        for key, value in post_template.items():
            try:
                post[key] = value(post_soup)
            except Exception:
                post[key] = None
        return post


    def get_post_comments(self, post_soup: BeautifulSoup) -> list:
        """
        Getting comments from post


        {'id': 682535,
        'parent_id': None,
        'root_comment_id': None,
        'likes_count': 0,
        'body': 'Отличная статья!',
        'html': '<p>Отличная статья!',
        'created_at': '2020-10-23T02:40:15.230+03:00',
        'hidden': False,
        'deep': 0,
        'date_formatted': 'вчера в 02:40',
        'user': {'id': 4146105, 'first_name': 'Арина', 'last_name': 'Смирнова', 'full_name': 'Арина Смирнова',
        'image': {'url': '/images/anonymous.png', 'width': 128, 'height': 128},
        'avatar': {'url': '/images/anonymous.png', 'width': 128, 'height': 128},
        'url': 'https://geekbrains.ru/users/4146105', 'is_online': False, 'confirmed': True}, 'children': [],
        'can_edit': False,
        'time_now': '2020-10-24T12:06:12.661+03:00',
        'can_hide': False,
        'can_thank': False,
        'is_answer': False,
        'can_mark_as_answer': False,
        'is_liked': False,
        'by_mentor': False,
        'by_teacher': False,
        'by_community_manager': False}

        """
        comments_api_url = "https://geekbrains.ru/api/v2/comments"
        comments_total = int(post_soup.find('comments').attrs.get('total-comments-count'))

        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
            'Range': f"0-{comments_total}",
        }

        commentable_id = int(post_soup.find('comments').attrs.get('commentable-id'))

        params = {
            'commentable_type': 'Post',
            'commentable_id': commentable_id,
            'order': 'desc',
        }

        response = requests.get(comments_api_url, headers=headers, params=params)
        json_comments_response = json.loads(response.text)
        comments = []
        #Рекурсию не делаем, т.к. по тз надо только имя, да текст комментария
        for json_comment in json_comments_response:
            comment = {
                'Comment_author_url': json_comment.get('comment').get('user').get('url'),
                'Comment_author': json_comment.get('comment').get('user').get('full_name'),
                'Comment_text': json_comment.get('comment').get('body'),
            }
            comments.append(comment)
        return comments


    def db_init(self):
        engine = create_engine('sqlite:///gb_blog.db')
        models.Base.metadata.create_all(bind=engine)
        SessionMaker = sessionmaker(bind=engine)
        self.db = SessionMaker()

    def db_close(self):
        db.close()
        pass

    def commit_to_db(self, post_data: dict):
        """
        *************************************DICT STRUCTURE*************************************
        url: https://geekbrains.ru/posts/bezopasnost-veb-novyj-fakultativ-ot-hacktory
        post_title: «Безопасность веб» — новый факультатив от Hacktory
        post_publish_date: 2020-10-23T11:48:00+03:00
        image_url: https://d2xzmw6cctk25h.cloudfront.net/geekbrains/public/ckeditor_assets/pictures/9860/retina-f0d622a24fa84ace868a3e5606fb1c09.png
        author: Geek Brains
        author_url: https://geekbrains.ru/users/63
        post_tags: ['web', 'программирование']
        comments: []


        Saving data to BD
        :param post_data:
        :return:
        """

        """
        *************************************DB STRUCTURE*************************************
        Post
        id = Column(Integer, autoincrement=True, primary_key=True)
        url = Column(String, unique=True, nullable=False)
        title = Column(String, unique=False, nullable=False)
        publish_date = Column(Datetime, unique=False, nullable=False)
        img_url = Column(String, unique=False, nullable=True)
        author_id = Column(Integer, ForeignKey('author.id'))
        author = relationship("Author", back_populates='posts')
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

        author = models.Author(name=post_data['author'], url=post_data['author_url'])
        # post = models.Post(url=post_data['url'], title=post_data['post_title'],  publish_date=post_data['post_publish_date'], img_url=post_data['image_url'], author=author)
        # self.db.add(post)
        self.db.add(author)
        self.db.commit()



if __name__ == '__main__':
    url = 'https://geekbrains.ru/posts?pages=56'
    parser = MagnitParser(url)
    parser.parse()