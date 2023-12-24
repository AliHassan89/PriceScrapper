#!/usr/bin/env python3
import json
from playwright.sync_api import expect, sync_playwright  # 1.37.0
from time import sleep


def scrape(page):
    url = "https://zakupy.auchan.pl/shop/list/8029?shType=id"
    api_url = "https://zakupy.auchan.pl/api/v2/cache/products"
    new_url = "https://zakupy.auchan.pl/api/v2/cache/products?listId=8029&itemsPerPage=500&page=1&cacheSegmentationCode=019_DEF&hl=pl"
    done = False
    items = []

    def handle(route, request):
        route.continue_(url=new_url)

    page.route("https://zakupy.auchan.pl/api/v2/cache/products*", handle)

    def handle_response(response):
        nonlocal done
        if response.url.startswith(api_url):
            items.append(response.json())
            done = True

    page.on("response", handle_response)
    page.goto(url)
    page.click("#onetrust-accept-btn-handler")

    while not done:
        page.keyboard.press("PageDown")
        sleep(0.2)  # save a bit of CPU

    results = []
    for x in items:
        for y in x["results"]:
            product_info = {"product_name": y["defaultVariant"]["name"],
                            "price": y["defaultVariant"]["price"]["gross"]}
            results.append(product_info)
            with open("../../output_auchan.json", "w") as f:
                json.dump(results, f)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    scrape(browser.new_page())
    browser.close()
