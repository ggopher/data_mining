# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class YoulaAutoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()
    url = scrapy.Field()
    features = scrapy.Field()
    description = scrapy.Field()
    owner = scrapy.Field()
    phone_num = scrapy.Field()

class HHVacancyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    owner_url = scrapy.Field()

class HHCompaniesItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    company_url = scrapy.Field()
    areas = scrapy.Field()
    description = scrapy.Field()