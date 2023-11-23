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
                  'https://www.carrefour.pl/dania-gotowe-i-przystawki?page=0',
                  'https://www.carrefour.pl/dania-gotowe-i-przystawki?page=0'
                  ]
    class_list1 = ['jss304', 'jss300 jss3', 'MuiTypography-root MuiTypography-body1', 'MuiButtonBase-root jss328',
                   'jss331', 'MuiTypography-root jss144 MuiTypography-h1',
                   'MuiTypography-root jss144 jss332 MuiTypography-h3',
                   'MuiTypography-root jss144 jss337 MuiTypography-h3']
    carrefour_map = {start_urls[0]: class_list1,
                     start_urls[1]: class_list1,
                     start_urls[2]: class_list1}

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
        product_containers = soup.find_all('div', class_=self.class_list1[0])
        max_pages_container = soup.find('div', class_=self.class_list1[1])\
            .find('p', class_=self.class_list1[2]).get_text()
        max_pages = int(re.findall(r'\d+', max_pages_container)[0])

        product_names = []
        product_prices = []
        for product_container in product_containers:
            product_names.append(product_container.find('h3', class_=self.class_list1[3]).get_text())
            full_price = product_container.find('div', class_=self.class_list1[4])
            price = full_price.find(class_=self.class_list1[5]).get_text()
            decimal = full_price.find(class_=self.class_list1[6]).get_text()
            currency = full_price.find(class_=self.class_list1[7]).get_text()
            product_prices.append(price + "." + decimal + currency)

        # Yield the extracted data
        for name, price in zip(product_names, product_prices):
            yield {
                'product_name': name,
                'price': price
            }

        # go to next page
        page_number += 1
        if page_number >= 2:
            return
        next_page = main_url+str(page_number)
        yield scrapy.Request(
            url=next_page,
            callback=self.parse,
            meta={"proxy": "http://007481b7bc40070104e3ac9e5e97fec6434a0161:@proxy.zenrows.com:8001"},
            cb_kwargs=dict(main_url=main_url, page_number=page_number),
        )
