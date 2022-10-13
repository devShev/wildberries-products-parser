import copy
import csv
from datetime import datetime
from time import sleep

from progress.bar import IncrementalBar
from requests import Session

from src.models import BaseJSONResponse, Product
from src.terminal import Terminal


class Parser:
    # request
    __session: Session
    __url: str
    __params = {
        'page': 1
    }

    # data
    __data: list[Product] = []
    __cache: list[Product] = []

    # config
    __MAX_PAGE: int = 100

    def __init__(self, url):
        self.__url = url

    def __start_session(self):
        self.__session = Session()

    def __save_cache(self):
        self.__cache = copy.copy(self.__data)

    def __get_json_response(self):
        return self.__session.get(self.__url, params=self.__params).text

    def __set_page_parse(self, page: int):
        self.__params['page'] = page

    def __get_current_page(self):
        return self.__params['page']

    def __update_data_from_json(self, json: str, all_pages: bool = False):
        self.__save_cache()

        base = BaseJSONResponse.parse_raw(json)  # create Response Object
        data = base.get_data()  # extract data from response
        data.create_url_for_products()  # create url for products in data
        products = data.get_products()  # get product

        if not all_pages:
            self.__data = copy.copy(products)
        else:
            self.__data.extend(products)

    def __parse(self, all_pages: bool = False):
        print()
        bar = IncrementalBar('Парсинг страниц: ', max=self.__MAX_PAGE)

        try:
            while self.__get_current_page() <= self.__MAX_PAGE:
                if all_pages:
                    bar.next()

                json = self.__get_json_response()
                self.__update_data_from_json(json, all_pages=all_pages)

                if all_pages:
                    current_page = self.__get_current_page()
                    if current_page < self.__MAX_PAGE:
                        self.__set_page_parse(current_page + 1)
                    else:
                        bar.finish()
                        break

                if not all_pages:
                    break

        except BaseException as e:
            print(f'\n{Terminal.WARN}Ошибка парсинга!{Terminal.NORMAL}')
            print(f'{Terminal.WARN}{e}')
        else:
            print(f'\n{Terminal.INFO}Парсинг! [{datetime.now().strftime("%H:%M %d-%m-%Y")}]{Terminal.NORMAL}')

    def __check_update(self):
        current_cache_set = set(self.__cache)
        current_data_set = set(self.__data)

        diff_elements_set = current_data_set.difference(current_cache_set)

        if diff_elements_set:
            print(f'{Terminal.INFO}Есть изменения:{Terminal.NORMAL}\n')
            for el in diff_elements_set:
                el.print()

    def set_max_page(self, page: int):
        if page > 100:
            answer = input(f'Значения больше 100 могут вызывать ошибки!'
                           f' Вы уверены что хотите присвоить значение \'{page}\'? ( y / n )/n >> ')
            if answer.lower() not in ('y', 'yes'):
                return
        self.__MAX_PAGE = page

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
                print(f'\n{Terminal.WARN}Ошибка записи!{Terminal.NORMAL}')
                print(f'{Terminal.WARN}{e}')
            else:
                print(f'\n{Terminal.INFO}Данные сохранены в {filepath}!{Terminal.NORMAL}\n')
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
            print(f'\n{Terminal.WARN}Ошибка чтения файла!{Terminal.NORMAL}')
            print(f'{Terminal.WARN}{e}')
        else:
            self.__data = copy.copy(data)
            print(f'\n{Terminal.INFO}Данные загружены из \'{filepath}\'!{Terminal.NORMAL}\n')

    def print_data(self):
        if self.__data:
            for product in self.__data:
                product.print()
        else:
            print(f'\n{Terminal.WARN}Нечего выводить!{Terminal.NORMAL}')

    def parse(self, all_pages: bool = False):
        self.__start_session()
        self.__parse(all_pages=all_pages)
        self.__session.close()

    def parse_page(self, page: int):
        self.__set_page_parse(page=page)

        self.__start_session()
        self.__parse()
        self.__session.close()

        self.__set_page_parse(page=1)

    def run(self, all_pages: bool = False, export_csv: bool = False, repeat: bool = False, timer: int = 60):
        self.__start_session()

        while True:
            self.__parse(all_pages=all_pages)

            if not export_csv:
                self.__check_update()
            else:
                self.save_csv()

            if not repeat:
                break

            sleep(timer)

        self.__session.close()
