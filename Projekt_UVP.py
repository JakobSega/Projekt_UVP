import csv
import os
import requests
import re

page_number = 1
car_number = 1
cars_url = f"https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&isSearchRequest=true&makeModelVariant1.makeId=9000&makeModelVariant1.modelId=30&pageNumber={page_number}&ref=srpNextPage&scopeId=C&sortOption.sortBy=relevance&refId=3e6d2e0e-8fd8-8a33-ceb3-956b170f5017"
cars_directory = "cars"
main_cars_filename = f"cars{page_number}.html"
secondary_cars_filename = f"secondary_cars{car_number}.html"


def download_url_as_string(url):

    page_content = requests.get(url)
    return page_content.text

def save_string_to_to_file(text, directory, filename):
    
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None

def save_html(url, directory, filename):
    
    page_content = download_url_as_string(url)
    save_string_to_to_file(page_content, directory, filename)

def main(redownload=True, reparse=True):

    if redownload:
        save_html(cars_url, cars_directory, cars_filename)