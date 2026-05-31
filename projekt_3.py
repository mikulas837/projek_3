"""
projekt_3.py: 
author: Mikuláš Říha
email: riha239845@mot.sps-dopravni.cz
"""

import sys
import csv
import requests
from bs4 import BeautifulSoup

# Hlavní URL adresa pro doplňování odkazů obcí
BASE_URL = "https://volby.cz/pls/ps2017nss/"


def main():
    # 1. KONTROLA ARGUMENTŮ
    # Program vyžaduje přesně 2 argumenty + název skriptu samotného = celkem 3 prvky v sys.argv
    if len(sys.argv) != 3:
        print("Chyba: Zadejte přesně dva argumenty!")
        print("Příklad: python projekt_3.py <URL_odkaz> <vystupni_soubor.csv>")
        sys.exit(1)

    url_hlavni = sys.argv[1]
    jmeno_souboru = sys.argv[2]

    # Jednoduché ověření, zda odkaz vede na správný web a soubor má příponu .csv
    if "volby.cz" not in url_hlavni:
        print("Chyba: První argument musí být platný odkaz z volby.cz!")
        sys.exit(1)

    if not jmeno_souboru.endswith(".csv"):
        print("Chyba: Druhý argument musí končit příponou .csv!")
        sys.exit(1)

    print(f"ZÍSKÁVÁM DATA Z URL: {url_hlavni}")

    # Načtení hlavní stránky okresu
    odpoved = requests.get(url_hlavni)
    if odpoved.status_code != 200:
        print("Chyba při načítání hlavní stránky.")
        sys.exit(1)

    soup_hlavni = BeautifulSoup(odpoved.text, "html.parser")
    
    # Najdeme všechny řádky tabulky, kde jsou obce
    vsechny_radky = soup_hlavni.find_all("tr")
    
    seznam_obci_data = []
    seznam_stran = []
    prve_nacteni = True

    # 2. PROCHÁZENÍ HLAVNÍ TABULKY S OBCEMI
    for radek in vsechny_radky:
        # Hledáme buňku s třídou 'cislo', kde je kód obce a odkaz na detail
        td_kod = radek.find("td", {"class": "cislo"})
        
        # Pokud řádek neobsahuje kód obce, přeskočíme ho
        if td_kod is None:
            continue
            
        odkaz_a = td_kod.find("a")
        if odkaz_a is None:
            continue

        kod_obce = td_kod.text.strip()
        
        # Název obce je ve stejném řádku v buňce s třídou 'overflow_name'
        td_nazev = radek.find("td", {"class": "overflow_name"})
        nazev_obce = td_nazev.text.strip()

        # Poskládání celé URL adresy pro detail obce
        url_detail_obce = BASE_URL + odkaz_a["href"]
        print(f"ZÍSKÁVÁM DATA Z URL: {url_detail_obce}")

        # Načtení detailu konkrétní obce
        odpoved_obec = requests.get(url_detail_obce)
        soup_obec = BeautifulSoup(odpoved_obec.text, "html.parser")

        # 3. SCRAPOVÁNÍ DAT Z DETAILU OBCE (Voliči, obálky, hlasy)
        # Vyčištění čísel od nezlomitelných mezer (\xa0), které web používá jako oddělovač tisíců
        volici_text = soup_obec.find("td", {"headers": "sa2"}).text
        volici = volici_text.replace("\xa0", "").strip()

        obalky_text = soup_obec.find("td", {"headers": "sa3"}).text
        obalky = obalky_text.replace("\xa0", "").strip()

        platne_hlasy_text = soup_obec.find("td", {"headers": "sa6"}).text
        platne_hlasy = platne_hlasy_text.replace("\xa0", "").strip()

        # Vytvoření základního slovníku pro řádek obce
        radek_data = {
            "code": kod_obce,
            "location": nazev_obce,
            "registered": volici,
            "envelopes": obalky,
            "valid": platne_hlasy
        }

        # 4. ZÍSKÁVÁNÍ HLASŮ PRO KANDIDUJÍCÍ STRANY
        # Strany jsou v tabulkách s třídou 'table'. První tabulka na stránce je sumář, ty další (druhá a třetí) jsou strany.
        vsechny_tabulky = soup_obec.find_all("table", {"class": "table"})
        tabulky_se_stranami = vsechny_tabulky[1:]

        for tabulka in tabulky_se_stranami:
            radky_stran = tabulka.find_all("tr")
            for radek_strany in radky_stran:
                td_jmeno_strany = radek_strany.find("td", {"class": "overflow_name"})
                
                if td_jmeno_strany is not None:
                    jmeno_strany = td_jmeno_strany.text.strip()
                    
                    # Hlasy jsou v buňce, která má v headers buď 'sa2' nebo 'sb2' (podle toho, v jakém je tabulka sloupci)
                    td_hlasy = radek_strany.find("td", {"headers": "t1sa2"})
                    if td_hlasy is None:
                        td_hlasy = radek_strany.find("td", {"headers": "t2sa2"})
                    if td_hlasy is None:
                        td_hlasy = radek_strany.find("td", {"headers": "t1sb2"})
                    if td_hlasy is None:
                        td_hlasy = radek_strany.find("td", {"headers": "t2sb2"})

                    # Vyčištění a uložení počtu hlasů
                    hlasy = td_hlasy.text.replace("\xa0", "").strip()
                    
                    # Uložíme hlasy do dat obce
                    radek_data[jmeno_strany] = hlasy

                    # Při prvním průchodu si uložíme názvy stran pro hlavičku CSV souboru
                    if prve_nacteni:
                        seznam_stran.append(jmeno_strany)

        prve_nacteni = False
        seznam_obci_data.append(radek_data)

    # 5. ZÁPIS DO CSV SOUBORU
    print(f"UKLÁDÁM DATA DO SOUBORU: {jmeno_souboru}")
    
    hlavicka_csv = ["code", "location", "registered", "envelopes", "valid"] + seznam_stran

    with open(jmeno_souboru, mode="w", newline="", encoding="utf-8") as soubor:
        zapisovac = csv.DictWriter(soubor, fieldnames=hlavicka_csv)
        zapisovac.writeheader()
        
        for data_obce in seznam_obci_data:
            zapisovac.writerow(data_obce)

    print(f"DOKONČUJI: {sys.argv[0]}")


if __name__ == "__main__":
    main()