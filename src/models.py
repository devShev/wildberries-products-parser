from typing import Optional

from pydantic import BaseModel

from src.terminal import Terminal


class Product(BaseModel):
    id: int
    name: str
    brand: str
    sale: int
    priceU: int
    salePriceU: int
    url: Optional[str] = None

    def __hash__(self):
        return hash(self.id)

    def create_url(self):
        self.url = f'https://www.wildberries.by/catalog/{self.id}/detail.aspx?targetUrl=GP'

    def print(self):
        print(f'Бренд: {self.brand}')
        print(f'Имя: {self.name}')
        print(f'Цена: {self.priceU}')
        print(f'URL: {Terminal.GREEN}{self.url}{Terminal.NORMAL}\n')


class BaseData(BaseModel):
    products: list[Product]

    def create_url_for_products(self):
        for product in self.products:
            product.create_url()

    def get_products(self):
        return self.products


class BaseJSONResponse(BaseModel):
    state: int
    version: int
    data: BaseData

    def get_data(self):
        return self.data
