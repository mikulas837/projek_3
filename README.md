# Projekt_3

## Představení projektu

Tento program slouží k automatickému stahování a zpracování výsledků z parlamentních voleb v roce 2017. Skript dokáže projít libovolný okres, který si zvolíte na oficiálních stránkách [volby.cz](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ) vytáhnout z něj data pro jednotlivé obce a vše exportovat do formátu .csv.

## Spuštění skriptu

Před spuštěním projektu si nainstalujte potřebné knihovny uvedené v souboru `requirements.txt`. Program komunikuje přes příkazovou řádku a ke svému spuštění potřebuje přesně dva povinné parametry:
1. Odkaz na detail vybraného územního celku
2. Název výstupního souboru s koncovkou .csv

```bash
python projekt_3.py <odkaz_uzemniho_celku> <vystupni_soubor>
```

Výstupem bude soubor `.csv` s výsledky voleb.

## Příklad z praxe

Pro okres Cheb:

1. **Odkaz** -> `https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=5&xnumnuts=4101`
2. **Název výstupního souboru** -> `cheb_volby17.csv`
### Kousek z výstupu:
```text
code,location,registered,envelopes,valid,Občanská demokratická strana,Řád národa - Vlastenecká unie,Česká strana sociálně demokratická...
554499,Aš,9766,4289,4254,271,36,216...
554502,Dolní Žandov,943,532,528,31,3,23...
554511,Drmoul,769,486,481,49,2,22...
