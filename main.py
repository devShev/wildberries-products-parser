import os

from src.parser import Parser

url = os.environ.get("URL")

parser = Parser(url)

parser.parse(all_pages=False)
parser.save_csv()
