import csv
import os
import requests
import re

Page_number = 1
Car_number = 1
Cars_url = f"https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&isSearchRequest=true&makeModelVariant1.makeId=9000&makeModelVariant1.modelId=30&pageNumber={page_number}&ref=srpNextPage&scopeId=C&sortOption.sortBy=relevance&refId=3e6d2e0e-8fd8-8a33-ceb3-956b170f5017"
Cars_directory = "cars"
Main_cars_filename = f"main_cars{Page_number}.html"
Secondary_cars_filename = f"secondary_cars{Car_number}.html"


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


def save_main_htmls(url_page_number, directory, filename_page_number, page_number, number):
    """Funkcija shrani vsebino spletne strani na naslovih "url_page_number" v datoteko
    "directory"/"filename_page_number"."""
    while page_number <= number:
        save_html(url_page_number, directory, filename_page_number)
        page_number += 1


def save_secondary_htmls(info_from_blocks, directory, filename_car_number, car_number):
    """Funkcija sprejme seznam slovarjev, ki vsebujejo povezave in shrani vsebino spletnih strani v datoteko "directory"/"filename_car_number"."""
    for i in info_from_blocks:
        save_html(i["povezava"], directory, filename_car_number)
        car_number +=1


def make_main_blocks(directory, main_filename):
    """Funkcija sprejme html dokument, ki se nahaja na lokaciji "directory"/"main_filename"
    in izlušči izseke s povezavo in id-jem v seznam."""

    path = os.path.join(directory, main_filename)
    vzorec = r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="https://suchen\.mobile\.de/fahrzeuge/details.*?" data-listing-id="\d+"'
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


#blocks = make_all_main_blocks(cars_directory, main_cars_filename, page_number, 2)


#print(blocks[1])


def get_info_from_block(block):
    """Funkcija iz niza za posamezn blok izlošči povezavo in id."""
    povezava = re.search(r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="(https://suchen\.mobile\.de/fahrzeuge/details.*?)" data-listing-id="\d+"', block)
    id = re.search(r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="https://suchen\.mobile\.de/fahrzeuge/details.*?" data-listing-id="(\d+)"', block)
    return {"id": id.group(1), "povezava": povezava.group(1)}

#print(get_info_from_block(blocks[1]))


def get_info_from_blocks(directory, main_filename_page_number, page_number, number=50):
    blocks = make_all_main_blocks(directory, main_filename_page_number, page_number, number=50)
    povezave_ids = [get_info_from_block(block) for block in blocks]
    return povezave_ids

print(get_info_from_blocks(Cars_directory, Main_cars_filename, Page_number, 2))


#def get_info_from_html():


#def main(redownload=True, reparse=True):
#
#   if redownload:
#      save_html(cars_url, cars_directory, main_cars_filename)