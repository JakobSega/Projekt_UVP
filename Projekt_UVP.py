import csv
import os
import requests
import re
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc




Number_of_pages = 1
Starting_page_number = 1
#Cars_url = f"https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&isSearchRequest=true&makeModelVariant1.makeId=9000&makeModelVariant1.modelId=30&pageNumber={Page_number}&ref=srpNextPage&scopeId=C&sortOption.sortBy=relevance&refId=3e6d2e0e-8fd8-8a33-ceb3-956b170f5017"
Cars_directory = "cars"
#Main_cars_filename = f"main_cars{Page_number}.html"
Csv_filename = "cars.csv"


def download_url_as_string(url):
    """Funkcija kot argument sprejme url in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        page_content = requests.get(url, headers=headers)
        page_content.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Spletna stran trenutno ni dosegljiva:", e)
        return None
    return page_content.text



def download_url_as_string_selenium(url):
    """Funkcija kot argument sprejme url in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        #DRIVER_PATH = "C:\Users\blin\AppData\Local\Programs\Python\Python311\Lib\site-packages\undetected_chromedriver\"
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        page_content = driver.page_source
        driver.quit()

        return page_content
    except Exception as e:
        print("Spletna stran trenutno ni dosegljiva:", e)
        return None

#niz = download_url_as_string_selenium(Cars_url)
#print(niz)

def save_string_to_file(text, directory, filename):
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
    #print(page_content)
    save_string_to_file(page_content, directory, filename)


#def save_secondary_html(url, directory, filename):
#    """Funkcija shrani vsebino spletne strani na naslovu "url" v datoteko
#    "directory"/"filename"."""
#
#    page_content = download_url_as_string(url)
#    #print(page_content)
#    save_string_to_file(page_content, directory, filename)


def save_main_htmls(directory, page_number, number):
    """Funkcija shrani vsebino spletne strani na naslovih "cars_url" v datoteko
    "directory"/"filename_page_number"."""
    while page_number <= number:
        cars_url = f"https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&isSearchRequest=true&makeModelVariant1.makeId=9000&makeModelVariant1.modelId=30&pageNumber={page_number}&ref=srpNextPage&scopeId=C&sortOption.sortBy=relevance&refId=3e6d2e0e-8fd8-8a33-ceb3-956b170f5017"
        cars_filename = f"main_cars{page_number}.html"
        save_html(cars_url, directory, cars_filename)
        page_number += 1


def save_secondary_htmls(info_from_blocks, directory):
    """Funkcija sprejme množico, ki vsebuje id-je in shrani vsebino spletnih strani v datoteko "directory"/"filename_car_number"."""
    car_number = 1
    for i in info_from_blocks:
        ID = i
        Secondary_cars_filename = f"secondary_cars{car_number}.html"
        print(ID)
        Secondary_cars_url = f"https://www.mobile.de/svc/a/{ID}"#https://www.mobile.de/svc/a/342813417
        save_html(Secondary_cars_url, directory, Secondary_cars_filename)
        car_number +=1  


def make_main_blocks(directory, main_filename):
    """Funkcija sprejme html dokument, ki se nahaja na lokaciji "directory"/"main_filename"
    in izlušči izseke z id-jem v seznam."""

    path = os.path.join(directory, main_filename)
    vzorec = r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="https://suchen\.mobile\.de/fahrzeuge/details.*?" data-listing-id="\d+"'
    with open(path, "r", encoding="UTF8") as doc:
        str = doc.read()
    return re.findall(vzorec, str, flags=re.DOTALL)


def make_all_main_blocks(directory, page_number, number):
    """Funkcija sprejme "seznam" dokumentov, ki so oštevilčeni s "page_number" in vrne seznam blokov, ki vsebujejo id."""

    sez = []
    while page_number <= number:
        main_filename = f"main_cars{page_number}.html"
        sez.extend(make_main_blocks(directory, main_filename))
        page_number += 1
    return sez

#blocks = make_all_main_blocks(cars_directory, main_cars_filename, page_number, 2)
#print(blocks[1])

def get_info_from_block(block):
    """Funkcija iz niza za posamezn blok izlušči id."""
    #povezava = re.search(r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="(https://suchen\.mobile\.de/fahrzeuge/details.*?)" data-listing-id="\d+"', block)
    id = re.search(r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="https://suchen\.mobile\.de/fahrzeuge/details.*?" data-listing-id="(\d+)"', block)
    #return {"id": id.group(1)} #, povezava": povezava.group(1)"""
    return id.group(1) #, povezava": povezava.group(1)"""

#print(get_info_from_block(blocks[1]))


def get_info_from_blocks(directory, page_number, number):
    """Funkcija iz seznama blokov izlušči množico id-jev."""
    blocks = make_all_main_blocks(directory, page_number, number)
    info_from_blocks = {get_info_from_block(block) for block in blocks}
    return info_from_blocks

#seznam = get_info_from_blocks(Cars_directory, Main_cars_filename, Page_number, 2)


def make_secondary_blocks(directory, car_number):
    """Funkcija sprejme html dokument, ki se nahaja na lokaciji "directory"/"secondary_cars'car_number'"
    in izlušči izsek z relevantnimi informacijami o avtomobilu."""
    secondary_filename = f"secondary_cars{car_number}.html"
    path = os.path.join(directory, secondary_filename)
    vzorec = r'.*"links"'
    with open(path, "r", encoding="UTF8") as doc:
        str = doc.read()
    return re.findall(vzorec, str, flags=re.DOTALL)

def make_all_secondary_blocks(directory, ids):
    """Funkcija iz skupine dokumentov, ki se nahajajo v direktoriju in ustrezajo vzorcu "secondary_cars'car_number'"
    izlušči izseke z relevantnimi informacijami o avtomobilih."""
    car_number = 1
    secondary_blocks = []
    while car_number <= len(ids):
        secondary_blocks.extend(make_secondary_blocks(directory, car_number))
        car_number += 1
    return secondary_blocks

def get_info_from_secondary_block(block):
    """Funkcija iz niza za posamezn blok izlušči relevantne informacije in jih vrne kot slovar."""
    mileage = re.search(r'{"label":"Mileage","tag":"mileage","value":"(.*) km"}', block)
    displacement = re.search(r'{"label":"Cubic Capacity","tag":"cubicCapacity","value":"(.*) ccm"}', block)     #PROBLEM
    power = re.search(r'{"label":"Power","tag":"power","value":"231 kW .\((.*) Hp\)"}', block)
    transmission = re.search(r'{"label":"Gearbox","tag":"transmission","value":"(.*)"}', block)
    registration = re.search(r'{"label":"First Registration","tag":"firstRegistration","value":".*\b\b\b\b"}', block)
    previous_owners = re.search(r'{"label":"Number of Vehicle Owners","tag":"numberOfPreviousOwners","value":"(\b*)"}', block)
    price = re.search(r'"localized":{"amount":"€(.*)","netAmount"', block)
    seller = re.search(r'"contact":{"type":"(.*)","country":"(.*)",', block)
    return {'mileage': mileage.group(1), 'displacement': displacement.group(1), 'power': power.group(1), 'transmission': transmission.group(1),
            'registration': registration.group(1), 'previous_owners': previous_owners.group(1), 'price': price.group(1), 'seller': seller.group(1)}

def get_info_from_secondary_blocks(secondary_blocks):
    """Funksija sprejme seznam nizov in vrne relevantne informacije kot seznam slovarjev."""
    info_from_secondary_blocks = []
    for block in secondary_blocks:
        info_from_secondary_blocks.extend(get_info_from_secondary_block(block))
        print(info_from_secondary_blocks)
    return info_from_secondary_blocks

def write_csv(fieldnames, rows, directory, filename):
    """Funkcija v csv datoteko podano s parametroma "directory"/"filename" zapiše
    vrednosti v parametru "rows" pripadajoče ključem podanim v "fieldnames."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return

def write_info_to_csv(info_from_secondary_blocks, directory, filename):
    """Funkcija vse podatke iz parametra "ads" zapiše v csv datoteko podano s
    parametroma "directory"/"filename". Funkcija predpostavi, da so ključi vseh
    slovarjev parametra ads enaki in je seznam ads neprazen."""
    assert info_from_secondary_blocks and (all(j.keys() == info_from_secondary_blocks[0].keys() for j in info_from_secondary_blocks))
    write_csv(info_from_secondary_blocks[0].keys(), info_from_secondary_blocks, directory, filename)


#print(seznam)
#print(seznam.count('366636334'))


#content = download_url_as_string("https://www.mobile.de/svc/a/366636334")
#print(content)


#save_secondary_htmls(seznam, Cars_directory)

ids = get_info_from_blocks(Cars_directory, Starting_page_number, Number_of_pages)
#print(ids)
#save_secondary_htmls(ids, Cars_directory)
secondary_blocks = make_all_secondary_blocks(Cars_directory, ids)
print("OK")
info = get_info_from_secondary_blocks(secondary_blocks)
write_info_to_csv(info, Cars_directory, Csv_filename)

#def main(redownload=True, reparse=True):
#    """Funkcija izvede celoten del pridobivanja podatkov:
#    1. Oglase prenese iz mobile.de
#    2. Lokalne html datoteke pretvori v lepšo predstavitev podatkov
#    3. Podatke shrani v csv datoteko
#    """
#    if redownload:
#        #save_main_htmls(Cars_directory, 1, Number_of_pages)
#        ids = get_info_from_blocks(Cars_directory, Starting_page_number, Number_of_pages)
#        print(ids)
#        save_secondary_htmls(ids, Cars_directory)
#        secondary_blocks = make_all_secondary_blocks(Cars_directory, ids)
#    if reparse:
#        print("OK")
#        info =get_info_from_secondary_blocks(secondary_blocks)
#        write_info_to_csv(info, Cars_directory, Csv_filename)
#
#if __name__ == '__main__':
#    main(True, True)