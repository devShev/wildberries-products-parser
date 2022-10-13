from src.parser import Parser

url = 'https://catalog.wb.ru/catalog/kitchen1/catalog?__tmp=by&appType=1&couponsGeo=12,7,3,21&curr=&dest=12358386,' \
      '12358403,-70563,-8139704&emp=0&lang=ru&locale=by&pricemarginCoeff=1&reg=0&regions=80,68,83,4,33,70,82,69,86,30' \
      ',40,48,1,22,66,31&spp=0&subject=869;993;998;1261;1345;1364;1371;1506;1774;1811;1825;2476;4560;4667;5061;5077' \
      ';5152;5955;6785;6965;6992'

parser = Parser(url)

parser.parse(all_pages=True)
parser.save_csv()
