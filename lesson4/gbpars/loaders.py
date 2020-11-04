import re
import base64
from urllib.parse import unquote
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader
from scrapy import Selector
from .items import YoulaAutoItem, HHVacancyItem, HHCompaniesItem

def search_owner_phone(itm):
    find_owner_phone = re.compile(r"phone%22%2C%22([0-9a-zA-Z]{33}w%3D%3D)%22%2C%22time")
    phone_encoded = re.findall(find_owner_phone, itm)
    # code-decode-code encryption))
    phone_decoded = base64.b64decode(base64.b64decode(unquote(phone_encoded[0]).encode('utf-8')))
    phone = phone_decoded.decode('utf-8')
    return phone

def search_owner_id(itm):
    owner_id = re.compile(r"youlaId%22%2C%22([0-9a-zA-Z]+)%22%2C%22avatar")
    dealer_id = re.compile("page%22%2C%22(https%3A%2F%2Fam.ru%2Fcardealers%2F[0-9a-zA-Z\S]+%2F%23info)"
                                "%22%2C%22salePointLogo")
    owner = re.findall(owner_id, itm)
    dealer = re.findall(dealer_id, itm)
    #if not private person, but dealer condition:
    owner = f'https://youla.ru/user/{owner[0]}' if owner else unquote(dealer[0])
    return owner


def get_tech_data(itm):
    tech_data = Selector(text=itm)
    return {tech_data.xpath('//div/div[1]/text()').get(): tech_data.xpath('//div/div[2]//text()').get()}


def tech_data_out(itms):
    tech_data = {itm for itm in itms if None not in itm}
    return tech_data


class YoulaAutoLoader(ItemLoader):
    default_item_class = YoulaAutoItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    tech_data_in = MapCompose(get_tech_data)
    tech_data_out = tech_data_out
    description_out = TakeFirst()
    owner_in = MapCompose(search_owner_id)
    owner_out = TakeFirst()
    phone_num_in = MapCompose(search_owner_phone)
    phone_num_out = TakeFirst()


def symbols_delete(itm):
    result = itm.replace('\xa0', '')
    return result


def list_to_string_with_space(itm):
    result = ' '.join(itm)
    return symbols_delete(result)


def create_owner_url(itm):
    result = f'https://hh.ru{itm[0]}'
    return result

class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = list_to_string_with_space
    salary_out = TakeFirst()
    description_in = list_to_string_with_space
    description_out = TakeFirst()
    skills_out = MapCompose(symbols_delete)
    owner_url_in = create_owner_url
    owner_url_out = TakeFirst()


class HHCompaniesLoader(ItemLoader):
    default_item_class = HHCompaniesItem
    url_out = TakeFirst()
    title_in = list_to_string_with_space
    title_out = TakeFirst()
    company_url_out = TakeFirst()
    field_of_work_out = MapCompose(symbols_delete)
    description_in = list_to_string_with_space
    description_out = TakeFirst()