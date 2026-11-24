#!/usr/bin/env python3
"""Połączenie rocznych plików JSON w jeden plik dla każdej tabeli.

Skrypt download_data_from_api.py zapisuje dane w osobnych plikach dla każdego roku
(np. posts_2014.json ... posts_2024.json). Do analizy w Sparku dane z jednej tabeli
łączone są w jeden plik all_<tabela>.json (np. all_posts.json), który następnie
jest wgrywany do bucketu Amazon S3.
"""

import json

import boto3

BUCKET_NAME = "bucket1-project-pw"
UPLOAD_TO_S3 = True

YEAR_LIST = [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014]
TABLE_LIST = ["users", "posts", "comments", "questions", "answers"]


def merge_json_files(file_names, output_file):
    """Wczytuje listy rekordów z kilku plików JSON i zapisuje je jako jedną listę."""
    result = []
    for file_name in file_names:
        with open(file_name, "r") as infile:
            result.extend(json.load(infile))  # każdy plik zawiera listę rekordów

    with open(output_file, "w") as output:
        json.dump(result, output)

    print(f"{output_file}: {len(result)} rekordów")


for table in TABLE_LIST:
    files = [f"{table}_{year}.json" for year in YEAR_LIST]
    output_file = f"all_{table}.json"
    merge_json_files(files, output_file)

    # wgranie połączonego pliku do bucketu Amazon S3
    if UPLOAD_TO_S3:
        boto3.client("s3").upload_file(output_file, BUCKET_NAME, output_file)
        print(f"Wgrano s3://{BUCKET_NAME}/{output_file}")
