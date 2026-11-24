#!/usr/bin/env python3
"""Pobranie danych z forum askubuntu.com przez API Stack Exchange i zapis w Amazon S3.

Skrypt uruchamiany w środowisku AWS Cloud9.

Jak działa:
  * dla każdej tabeli z listy TABLE_LIST (users, posts, comments, questions, answers)
    dane pobierane są osobno dla każdego roku z listy YEAR_LIST,
  * API zwraca maksymalnie 100 rekordów na stronę, więc skrypt pobiera kolejne strony
    (parametr "page") dopóki API zwraca "has_more" = True,
  * rekordy z jednego roku są łączone w jedną listę i zapisywane jako plik JSON
    <tabela>_<rok>.json - lokalnie oraz w buckecie Amazon S3.

Podział na lata zmniejsza rozmiar pojedynczego pobrania - jeśli wystąpi błąd
lub skończy się dzienny limit zapytań API, wystarczy ponowić pobieranie jednego roku.

Dane uwierzytelniające (OAuth 2.0) NIE są zapisane w kodzie - przed uruchomieniem
należy ustawić zmienne środowiskowe:
    export SE_ACCESS_TOKEN="..."
    export SE_KEY="..."
"""

import json
import os
import time
from datetime import datetime, timezone

import boto3
import requests

# ---------------------------------------------------------------------------
# Konfiguracja
# ---------------------------------------------------------------------------
ACCESS_TOKEN = os.environ.get("SE_ACCESS_TOKEN")  # token dostępu OAuth 2.0
KEY = os.environ.get("SE_KEY")  # klucz zarejestrowanej aplikacji
SITE = "askubuntu"  # forum, z którego pobierane są dane

BUCKET_NAME = "bucket1-project-pw"
SAVE_TO_S3 = True  # zapis w buckecie Amazon S3
SAVE_LOCALLY = True  # dodatkowy zapis pliku na dysku

YEAR_LIST = [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014]
TABLE_LIST = ["users", "posts", "comments", "questions", "answers"]


def match_filter(table):
    """Zwraca identyfikator filtra API dla danej tabeli.

    Filtry zostały utworzone na stronie https://api.stackexchange.com/docs/filters
    i ograniczają odpowiedź API wyłącznie do pól potrzebnych w analizie
    (mniej przesyłanych danych i szybsze pobieranie).
    """
    if table == "users":
        return "!)scTwI5VFU6uxVO1fI3d"
    elif table == "posts":
        return "!B8mcuA5T6c5-aJEXkp3KCTPKZie5xK"
    elif table == "comments":
        return "!)Q0(G)xa-ZX9y_ePgp-l-xr)"
    elif table == "questions":
        return "!DE*zk4rSaWQ-HGfNVh7m6rk)tX8HZLxQQweh3dW5W7h.x7M7rXv"
    elif table == "answers":
        return "!szz.51CUjr4j3D))YMWvt-irLpXu.Rt"
    else:
        return "default"


def year_to_timestamps(year):
    """Zamienia rok na zakres dat w formacie Unix timestamp (wymaganym przez API).

    Zwraca (początek roku, koniec roku), np. dla 2020: 01.01.2020 00:00:00 - 31.12.2020 23:59:59.
    Obliczenie na podstawie kalendarza uwzględnia lata przestępne.
    """
    from_date = int(datetime(year, 1, 1, tzinfo=timezone.utc).timestamp())
    to_date = int(datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp()) - 1
    return from_date, to_date


def download_table_for_year(table, year):
    """Pobiera wszystkie rekordy danej tabeli utworzone w danym roku (strona po stronie)."""
    from_date, to_date = year_to_timestamps(year)
    base_url = f"https://api.stackexchange.com/2.3/{table}"
    parameters = {
        "pagesize": 100,  # maksymalna liczba rekordów na stronę dopuszczana przez API
        "site": SITE,
        "filter": match_filter(table),
        "access_token": ACCESS_TOKEN,
        "key": KEY,
        "fromdate": from_date,
        "todate": to_date,
        "order": "desc",
    }

    records = []
    page = 1
    while True:
        parameters["page"] = page
        try:
            response = requests.get(base_url, params=parameters, timeout=10)
        except requests.exceptions.Timeout:
            # Brak odpowiedzi serwera - odczekanie i ponowienie zapytania o tę samą stronę
            print(f"Timeout ({table} {year}, strona {page}) - ponawiam za 5 s")
            time.sleep(5)
            continue

        data = response.json()

        # API zwraca błąd w polu "error_id" (np. przekroczony limit zapytań)
        if "error_id" in data:
            print(f"Błąd API: {data.get('error_name')} - {data.get('error_message')}")
            break

        records.extend(data["items"])

        # "backoff" - API prosi o odczekanie podanej liczby sekund przed kolejnym zapytaniem
        if "backoff" in data:
            time.sleep(data["backoff"] + 1)

        # "has_more" = False oznacza ostatnią stronę wyników
        if not data["has_more"]:
            break
        page += 1

    print(f"{table} {year}: pobrano {len(records)} rekordów "
          f"(pozostały limit zapytań: {data.get('quota_remaining')})")
    return records


def main():
    if not ACCESS_TOKEN or not KEY:
        print("Ustaw zmienne środowiskowe SE_ACCESS_TOKEN i SE_KEY")
        return

    s3_client = boto3.client("s3")

    for table in TABLE_LIST:
        for year in YEAR_LIST:
            records = download_table_for_year(table, year)
            json_file = json.dumps(records)  # konwersja listy rekordów na format JSON
            file_name = f"{table}_{year}.json"

            # zapis pliku w Amazon S3
            if SAVE_TO_S3:
                s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=json_file)
                print(f"Zapisano s3://{BUCKET_NAME}/{file_name}")

            # zapis pliku na dysku
            if SAVE_LOCALLY:
                with open(file_name, "w") as file:
                    file.write(json_file)


if __name__ == "__main__":
    main()
