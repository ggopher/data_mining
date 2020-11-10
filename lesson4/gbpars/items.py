# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbparsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class InstagramPostsItm(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()

class InstagramTagsItm(InstagramPostsItm):
    pass
