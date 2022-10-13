import copy
import csv
from datetime import datetime
from time import sleep

from requests import Session

from src.models import BaseJSONResponse, Product
from src.terminal import Terminal


class Parser:
    # request
    __session: Session
    __url: str = 'https://catalog.wb.ru/catalog/books/catalog?__tmp=by'
    __params: dict = {
        'appType': '1',
        'couponsGeo': '12,7,3,21',
        'curr': '',
        'dest': '12358386,12358403,-70563,-8139704',
        'emp': '0',
        'lang': 'ru',
        'locale': 'by',
        'pricemarginCoeff': '1',
        'reg': 0,
        'regions': '68,83,4,80,33,70,82,86,30,69,1,48,22,66,31,40',
        'spp': '0',
        'subject': '1312;2018;2076;3647;3733',
    }

    # data
    __data: list[Product] = []
    __cache: list[Product] = []

    def __start_session(self):
        self.__session = Session()

    def __save_cache(self):
        self.__cache = copy.copy(self.__data)

    def __get_json_response(self):
        return self.__session.get(self.__url, params=self.__params).text

    def __update_data_from_json(self, json: str):
        self.__save_cache()

        base = BaseJSONResponse.parse_raw(json)  # create Response Object
        data = base.get_data()  # extract data from response
        data.create_url_for_products()  # create url for products in data
        products = data.get_products()  # get product

        self.__data = copy.copy(products)

    def __parse(self):
        try:
            json = self.__get_json_response()
            self.__update_data_from_json(json)
        except BaseException as e:
            print(f'{Terminal.WARN}Ошибка парсинга!{Terminal.NORMAL}')
            print(f'{Terminal.WARN}{e}')
        else:
            print(f'{Terminal.INFO}Парсинг! [{datetime.now().strftime("%H:%M %d-%m-%Y")}]{Terminal.NORMAL}\n')

    def __check_update(self):
        current_cache_set = set(self.__cache)
        current_data_set = set(self.__data)

        diff_elements_set = current_data_set.difference(current_cache_set)

        if diff_elements_set:
            print(f'{Terminal.INFO}Есть изменения:{Terminal.NORMAL}\n')
            for el in diff_elements_set:
                el.print()

    def save_csv(self, filepath: str = 'data.csv'):
        if self.__data:
            try:
                with open(filepath, mode='w', encoding='utf-8') as file:
                    fields = ['id', 'name', 'brand', 'sale', 'priceU', 'salePriceU', 'url']

                    writer = csv.DictWriter(file, delimiter=',', lineterminator="\r", fieldnames=fields)
                    writer.writeheader()
                    for product in self.__data:
                        writer.writerow(product.dict())
            except BaseException as e:
                print(f'{Terminal.WARN}Ошибка записи!{Terminal.NORMAL}')
                print(f'{Terminal.WARN}{e}')
            else:
                print(f'{Terminal.INFO}Данные сохранены в {filepath}!{Terminal.NORMAL}\n')
        else:
            print(f'{Terminal.WARN}Нечего сохранять!{Terminal.NORMAL}')

    def load_csv(self, filepath: str = 'data.csv'):
        try:
            with open(filepath, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = []
                for row in reader:
                    data.append(Product.parse_obj(row))
        except BaseException as e:
            print(f'{Terminal.WARN}Ошибка чтения файла!{Terminal.NORMAL}')
            print(f'{Terminal.WARN}{e}')
        else:
            self.__data = data
            print(f'{Terminal.INFO}Данные загружены из \'{filepath}\'!{Terminal.NORMAL}\n')

    def print_data(self):
        if self.__data:
            for product in self.__data:
                product.print()
        else:
            print(f'{Terminal.WARN}Нечего выводить!{Terminal.NORMAL}')

    def parse(self):
        self.__start_session()
        self.__parse()
        self.__session.close()

    def run(self, export_csv: bool = False, repeat: bool = False, timer: int = 60):
        self.__start_session()

        while True:
            self.__parse()

            if not export_csv:
                self.__check_update()
            else:
                self.save_csv()

            if not repeat:
                break

            sleep(timer)

        self.__session.close()
