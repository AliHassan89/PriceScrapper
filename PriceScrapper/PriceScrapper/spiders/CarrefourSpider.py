import scrapy
import re
from bs4 import BeautifulSoup


class CarrefourSpider(scrapy.Spider):
    name = 'carrefour'
    start_urls = ['https://www.carrefour.pl/owoce-warzywa-ziola?page=0']
    current_url = ''
    page_number = 0
    class_list1 = ['jss304', 'jss300 jss3', 'MuiTypography-root MuiTypography-body1', 'MuiButtonBase-root jss328',
                   'jss331', 'MuiTypography-root jss144 MuiTypography-h1',
                   'MuiTypography-root jss144 jss332 MuiTypography-h3',
                   'MuiTypography-root jss144 jss337 MuiTypography-h3']
    carrefour_map = {'https://www.carrefour.pl/owoce-warzywa-ziola?page=0': class_list1}
    current_class_list = []

    def start_requests(self):
        for url in self.start_urls:
            current_url = url
            current_class_list = self.carrefour_map[url]
            self.page_number = 0
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"proxy": "http://007481b7bc40070104e3ac9e5e97fec6434a0161:@proxy.zenrows.com:8001"},
            )

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        product_containers = soup.find_all('div', class_='jss304')
        max_pages_container = soup.find('div', class_='jss300 jss3')\
            .find('p', class_='MuiTypography-root MuiTypography-body1').get_text()
        max_pages = int(re.findall(r'\d+', max_pages_container)[0])

        product_names = []
        product_prices = []
        for product_container in product_containers:
            product_names.append(product_container.find('h3', class_='MuiButtonBase-root jss328').get_text())
            full_price = product_container.find('div', class_='jss331')
            price = full_price.find(class_='MuiTypography-root jss144 MuiTypography-h1').get_text()
            decimal = full_price.find(class_='MuiTypography-root jss144 jss332 MuiTypography-h3').get_text()
            currency = full_price.find(class_='MuiTypography-root jss144 jss337 MuiTypography-h3').get_text()
            product_prices.append(price + "." + decimal + currency)

        # Yield the extracted data
        for name, price in zip(product_names, product_prices):
            yield {
                'product_name': name,
                'price': price
            }

        # go to next page
        self.page_number += 1
        if self.page_number >= 1:
            return
        next_page = 'https://www.carrefour.pl/owoce-warzywa-ziola?page='+str(self.page_number)
        yield scrapy.Request(
            url=next_page,
            callback=self.parse,
            meta={"proxy": "http://007481b7bc40070104e3ac9e5e97fec6434a0161:@proxy.zenrows.com:8001"},
        )
