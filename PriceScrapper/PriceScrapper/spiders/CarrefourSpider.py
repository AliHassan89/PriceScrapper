import scrapy
import re
from bs4 import BeautifulSoup


class CarrefourSpider(scrapy.Spider):
    name = 'carrefour'
    start_urls = ['https://www.carrefour.pl/artykuly-spozywcze?page=0',
                  'https://www.carrefour.pl/mleko-nabial-jaja?page=0',
                  'https://www.carrefour.pl/napoje?page=0',
                  'https://www.carrefour.pl/drogeria-kosmetyki-i-zdrowie?page=0',
                  'https://www.carrefour.pl/zdrowa-zywnosc?page=0',
                  'https://www.carrefour.pl/owoce-warzywa-ziola?page=0',
                  'https://www.carrefour.pl/mieso?page=0',
                  'https://www.carrefour.pl/mrozonki?page=0',
                  'https://www.carrefour.pl/wedliny-kielbasy?page=0',
                  'https://www.carrefour.pl/piekarnia-ciastkarnia?page=0',
                  'https://www.carrefour.pl/ryby-i-owoce-morza?page=0',
                  'https://www.carrefour.pl/dziecko?page=0',
                  'https://www.carrefour.pl/dla-zwierzat?page=0',
                  'https://www.carrefour.pl/dania-gotowe-i-przystawki?page=0'
                  ]
    div_map_1 = {'productContainer': 'jss304',
                 'paginationContainer': 'jss300 jss3',
                 'maxPagesClass': 'MuiTypography-root MuiTypography-body1',
                 'productNameClass': 'MuiButtonBase-root jss328',
                 'fullPriceContainer': 'jss331',
                 'mainPriceClass': 'MuiTypography-root jss144 MuiTypography-h1',
                 'decimalPriceClass': 'MuiTypography-root jss144 jss332 MuiTypography-h3',
                 'currencyClass': 'MuiTypography-root jss144 jss337 MuiTypography-h3'}

    div_map_2 = {'productContainer': 'jss314',
                 'paginationContainer': 'jss310 jss3',
                 'maxPagesClass': 'MuiTypography-root MuiTypography-body1',
                 'productNameClass': 'MuiButtonBase-root jss338',
                 'fullPriceContainer': 'jss341',
                 'mainPriceClass': 'MuiTypography-root jss144 MuiTypography-h1',
                 'decimalPriceClass': 'MuiTypography-root jss144 jss342 MuiTypography-h3',
                 'currencyClass': 'MuiTypography-root jss144 jss347 MuiTypography-h3'}

    div_map_3 = {'productContainer': 'jss301',
                 'paginationContainer': 'jss297 jss3',
                 'maxPagesClass': 'MuiTypography-root MuiTypography-body1',
                 'productNameClass': 'MuiButtonBase-root jss325',
                 'fullPriceContainer': 'jss328',
                 'mainPriceClass': 'MuiTypography-root jss144 MuiTypography-h1',
                 'decimalPriceClass': 'MuiTypography-root jss144 jss329 MuiTypography-h3',
                 'currencyClass': 'MuiTypography-root jss144 jss334 MuiTypography-h3'}

    carrefour_map = {start_urls[0]: div_map_1,
                     start_urls[1]: div_map_2,
                     start_urls[2]: div_map_2,
                     start_urls[3]: div_map_3,
                     start_urls[4]: div_map_2,
                     start_urls[5]: div_map_1,
                     start_urls[6]: div_map_3,
                     start_urls[7]: div_map_1,
                     start_urls[8]: div_map_1,
                     start_urls[9]: div_map_1,
                     start_urls[10]: div_map_1,
                     start_urls[11]: div_map_3,
                     start_urls[12]: div_map_3,
                     start_urls[13]: div_map_1}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"proxy": "http://007481b7bc40070104e3ac9e5e97fec6434a0161:@proxy.zenrows.com:8001"},
                cb_kwargs=dict(main_url=url, page_number=0),
            )

    def parse(self, response, main_url, page_number):
        soup = BeautifulSoup(response.text, 'html.parser')
        div_map = self.carrefour_map[main_url]
        product_containers = soup.find_all('div', class_=div_map['productContainer'])
        max_pages_container = soup.find('div', class_=div_map['paginationContainer']) \
            .find('p', class_=div_map['maxPagesClass']).get_text()
        max_pages = int(re.findall(r'\d+', max_pages_container)[0])

        product_names = []
        product_prices = []
        for product_container in product_containers:
            product_names.append(product_container.find('h3', class_=div_map['productNameClass']).get_text())
            full_price = product_container.find('div', class_=div_map['fullPriceContainer'])
            price = full_price.find(class_=div_map['mainPriceClass']).get_text()
            decimal = full_price.find(class_=div_map['decimalPriceClass']).get_text()
            currency = full_price.find(class_=div_map['currencyClass']).get_text()
            product_prices.append(price + "." + decimal + currency)

        # Yield the extracted data
        for name, price in zip(product_names, product_prices):
            yield {
                'product_name': name,
                'price': price
            }

        # go to next page
        page_number += 1
        if page_number >= max_pages:
            return
        next_page = main_url + str(page_number)
        yield scrapy.Request(
            url=next_page,
            callback=self.parse,
            meta={"proxy": "http://007481b7bc40070104e3ac9e5e97fec6434a0161:@proxy.zenrows.com:8001"},
            cb_kwargs=dict(main_url=main_url, page_number=page_number),
        )
