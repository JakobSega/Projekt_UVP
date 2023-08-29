import csv
import os
import requests
import re



Number_of_pages = 4
Starting_page_number = 1
Cars_directory = "cars"
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
    save_string_to_file(page_content, directory, filename)


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
        Secondary_cars_url = f"https://www.mobile.de/svc/a/{ID}"#https://www.mobile.de/svc/a/373790083
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


def get_info_from_block(block):
    """Funkcija iz niza za posamezn blok izlušči id."""

    id = re.search(r'data-testid="no-top"><a class="link--muted no--text--decoration result-item" href="https://suchen\.mobile\.de/fahrzeuge/details.*?" data-listing-id="(\d+)"', block)
    return id.group(1)


def get_info_from_blocks(directory, page_number, number):
    """Funkcija iz seznama blokov izlušči množico id-jev."""

    blocks = make_all_main_blocks(directory, page_number, number)
    info_from_blocks = {get_info_from_block(block) for block in blocks}
    return info_from_blocks


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
    
    result = {}
    
    mileage_match = re.search(r'{"label"\s*:\s*".*?",\s*"tag"\s*:\s*"mileage",\s*"value"\s*:\s*"(.*?)\s*km"}', block)
    if mileage_match:
        result['mileage'] = mileage_match.group(1)
    else:
        result['mileage'] = "ni podatka"

    displacement_match = re.search(r'{"label"\s*:\s*"Hubraum",\s*"tag"\s*:\s*"cubicCapacity",\s*"value"\s*:\s*"([\d.]+)\s*cm³"}', block)
    if displacement_match:
        result['displacement'] = displacement_match.group(1)
    else:
        result['displacement'] = "ni podatka"

    power_match = re.search(r'{"label":"Leistung","tag":"power","value":"([\d\s]+)\s*kW\s*\(([\d\s]+)\s*PS\)"}', block)
    if power_match:
        kw_value = power_match.group(1).replace(' ', '').replace('kW', '')
        ps_value = power_match.group(2).replace(' ', '').replace('PS', '')

        try:
            result['power_kW'] = int(kw_value)
            result['power_Hp'] = int(ps_value)
        except ValueError:
            result['power_kW'] = "ni podatka"
            result['power_Hp'] = "ni podatka"
    else:
        result['power_kW'] = "ni podatka"
        result['power_Hp'] = "ni podatka"

    transmission_match = re.search(r'{"label"\s*:\s*"Getriebe",\s*"tag"\s*:\s*"transmission",\s*"value"\s*:\s*"(.*?)"}', block)
    if transmission_match:
        transmission_value = transmission_match.group(1)
        if transmission_value == 'Automatik':
            result['transmission'] = 'Automatic'
        else:
            result['transmission'] = 'Manual'
    else:
        result['transmission'] = "ni podatka"

    registration_match = re.search(r'{"label"\s*:\s*"Erstzulassung",\s*"tag"\s*:\s*"firstRegistration",\s*"value"\s*:\s*"\d{2}/(\d{4})"}', block)
    if registration_match:
        result['registration'] = registration_match.group(1)
    else:
        result['registration'] = "ni podatka"

    previous_owners_match = re.search(r'{"label"\s*:\s*"Anzahl der Fahrzeughalter",\s*"tag"\s*:\s*"numberOfPreviousOwners",\s*"value"\s*:\s*"(\d+)"}', block)
    if previous_owners_match:
        result['previous_owners'] = previous_owners_match.group(1)
    else:
        result['previous_owners'] = "ni podatka"

    homologation_match = re.search(r'{"label":"HU","tag":"hu","value":"(\d{2}/\d{4})"}', block)
    if homologation_match:
        homologation_value = homologation_match.group(1)
        result['homologation'] = homologation_value
    else:
        result['homologation'] = "ni podatka"

    price_match = re.search(r'"localized":{"amount":"([\d.,\s]+)€"', block)
    if price_match:
        price_value = price_match.group(1).replace(' ', '').replace(',', '').replace('€', '')
        try:
            result['price'] = int(price_value)
        except ValueError:
            result['price'] = int(float(price_value)*1000)
    else:
        result['price'] = "ni podatka"

    seller_match = re.search(r'"contact"\s*:\s*{"type"\s*:\s*"(.*?)",\s*"country"\s*:\s*"(.*?)",', block)
    if seller_match:
        seller_value = seller_match.group(1)
        if seller_value == 'Händler':
            result['seller_type'] = 'Dealer'
        else:
            result['seller_type'] = 'Private seller'
        result['seller_country'] = seller_match.group(2)
    else:
        result['seller_type'] = "ni podatka"
        result['seller_country'] = "ni podatka"

    return result


def get_info_from_secondary_blocks(secondary_blocks):
    """Funksija sprejme seznam nizov in vrne relevantne informacije kot seznam slovarjev."""

    info_from_secondary_blocks = []
    for block in secondary_blocks:
        print("extending info")
        info_from_secondary_blocks.append(get_info_from_secondary_block(block))
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







def main(redownload_main=True, reparse_main=True, redownload_secondary=True, reparse_secondary=True):
    """Funkcija izvede celoten del pridobivanja podatkov:
    1. Oglase prenese iz mobile.de
    2. Lokalne html datoteke pretvori v lepšo predstavitev podatkov
    3. Podatke shrani v csv datoteko
    """

    if redownload_main:
        save_main_htmls(Cars_directory, Starting_page_number, Number_of_pages)
    if reparse_main:
        ids = get_info_from_blocks(Cars_directory, Starting_page_number, Number_of_pages)
    if redownload_secondary:
        save_secondary_htmls(ids, Cars_directory)
    if reparse_secondary:
        secondary_blocks = make_all_secondary_blocks(Cars_directory, ids)
        info = get_info_from_secondary_blocks(secondary_blocks)
        write_info_to_csv(info, Cars_directory, Csv_filename)


if __name__ == '__main__':
    main(False, True, True, True)