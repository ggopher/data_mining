"""
Пример структуры данных для файла:
            {
                "name": "имя категории",
                "code": "Код соответсвующий категории (используется в запросах)",
                # список словарей товаров соответсвующих данной категории
                "products": [{PRODUCT},  {PRODUCT}........]
            }
"""

import datetime
import json
import os
import requests
from time import sleep


class Parser_5ka():
    __CAT_URL = "https://www.5ka.ru/api/v2/categories/"
    __CAT_CODE = "parent_group_code"
    __CAT_NAME = "parent_group_name"

    __PRODUCT_PARAMS = {
        "records_per_page": 50,
    }

    __headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
    }

    __JSON_DIRECTORY = os.path.join(os.path.dirname(__file__), r"categories/")

    def __init__(self, start_url: str, headers: dict = None) -> None:
        self.__start_url = start_url
        if headers:
            self.__headers = headers

    def __save_to_json(self, json_to_save: dict, file_name: str = "nan") -> None:
        """
        Save a JSON object in dict form to a file.
        :param json_to_save: dict - JSON object to save.
        :param file_name: str - name for JSON file.
        :return: None
        """
        if not os.path.exists(self.__JSON_DIRECTORY):
            os.mkdir(self.__JSON_DIRECTORY)

        file_path = os.path.join(self.__JSON_DIRECTORY, f"{file_name}.json")

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_to_save, file, ensure_ascii=False, indent=4)

        print(f"saved file: {str(file_path)}")

    def __parse_products(self, url: str = None, category: str = None) -> list:
        """
        Parsing products
        :param url: str - URL to start.
        :param category: str Category ID, if needed only one category.
        :return: list - list of products.
        """
        if not url:
            url = self.__start_url

        params = self.__PRODUCT_PARAMS
        if category:
            params.update({"categories": category})

        # Parse all product pages
        products = []
        while url:
            # To avoid server crash and IP blocking
            sleep(0.5)

            response = requests.get(url, headers=self.__headers, params=params)
            response = json.loads(response.text)

            products.extend(response["results"])

            url = response["next"]


        print(f"Parsed category with id {category}.")

        return products

    def get_prod_by_cat(self, *args, **kwargs) -> None:
        """
        Main method to parse
        return: None
        """
        print("Start working.")

        categories = self.__parse_cat()

        for category in categories:
            products = self.__parse_products(
                category=category[self.__CAT_CODE], *args, **kwargs,)

            if not products:
                print("Empty category!.")
                continue

            result = {
                "date_created": datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S"),
                "category": category[self.__CAT_NAME],
                "category_id": category[self.__CAT_CODE],
                "products": products,
            }

            self.__save_to_json(result, file_name=category[self.__CAT_NAME])

            # print("Work finished.")


    def __parse_cat(self) -> list:
        """
        Getting list of categories
        :return: list of categories
        """
        response = requests.get(self.__CAT_URL, headers=self.__headers)
        categories = json.loads(response.text)
        print(f"Parsed {len(categories)} categories.")
        return categories


if __name__ == '__main__':
    URL = "https://5ka.ru/api/v2/special_offers/"
    parser = Parser_5ka(URL)
    parser.get_prod_by_cat()