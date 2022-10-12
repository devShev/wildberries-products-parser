from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    brand: str
    sale: int
    priceU: int
    salePriceU: int

    def __hash__(self):
        return hash(self.id)

    def print(self):
        print(f'Бренд: {self.brand}')
        print(f'Имя: {self.name}')
        print(f'Цена: {self.priceU}')
        print()


class BaseData(BaseModel):
    products: list[Product]


class BaseJSONResponse(BaseModel):
    state: int
    version: int
    data: BaseData
