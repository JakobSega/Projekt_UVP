import csv
import os
import requests
import re

page_number = 1
car_number = 1
cars_url = f"https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&isSearchRequest=true&makeModelVariant1.makeId=9000&makeModelVariant1.modelId=30&pageNumber={page_number}&ref=srpNextPage&scopeId=C&sortOption.sortBy=relevance&refId=3e6d2e0e-8fd8-8a33-ceb3-956b170f5017"
cars_directory = "cars"
main_cars_filename = f"main_cars{page_number}.html"
secondary_cars_filename = f"secondary_cars{car_number}.html"


def download_url_as_string(url):
    """Funkcija kot argument sprejme url in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        headers = {"User-Agent": "Chrome/111.0.5563.111"}
        page_content = requests.get(url)
    except requests.exceptions.RequestException:
        print("Spletna stran trenutno ni dosegljiva.")
        return None
    return page_content.text


def save_string_to_to_file(text, directory, filename):
    """Funkcija zapiše vrednost parametra "text" v novo ustvarjeno datoteko
    locirano v "directory"/"filename", ali povozi obstoječo. V primeru, da je
    niz "directory" prazen datoteko ustvari v trenutni mapi.
    """

    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None


def save_html(url, directory, filename):
    """Funkcija shrani vsebino spletne strani na naslovu "url" v datoteko
    "directory"/"filename"."""

    page_content = download_url_as_string(url)
    save_string_to_to_file(page_content, directory, filename)


def make_main_blocks(directory, main_filename):
    """Funkcija sprejme html dokument, ki se nahaja na lokaciji "directory"/"main_filename"
    in izlušči izseke s povezavo in id-jem v seznam."""

    path = os.path.join(directory, main_filename)
    vzorec = r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="(https://suchen\.mobile\.de/fahrzeuge/details.*?)" data-listing-id="(\d+)"'
    with open(path, "r", encoding="UTF8") as doc:
        str = doc.read()
    return re.findall(vzorec, str, flags=re.DOTALL)


def make_all_main_blocks(directory, main_filename_page_number, page_number, number=50):
    """Funkcija sprejme "seznam" dokumentov, ki so oštevilčeni s "page_number" in vrne seznam blokov, ki vsebujejo povezavo in id."""
    
    sez = []
    while page_number <= number and page_number <= 50:
        sez.extend(make_main_blocks(directory, main_filename_page_number))
        page_number += 1
    return sez


sez = make_all_main_blocks(cars_directory, main_cars_filename, page_number, 2)
print(sez)


#def main(redownload=True, reparse=True):
#
#   if redownload:
#      save_html(cars_url, cars_directory, main_cars_filename)